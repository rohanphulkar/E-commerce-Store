from django.shortcuts import render,redirect
from .models import Product,Order,Review,Wishlist,Cart,CartItem,ProductImage
from django.shortcuts import get_object_or_404
import stripe,razorpay
from decouple import config
from django.db.models import Q,Avg
from .helper import sendOrderEmail

stripe.api_key=config("STRIPE_API_KEY")

def shop(request):
    search = request.GET.get('search', None)
    if search:
        products = Product.objects.filter(name__icontains=search)
    else:
        products = Product.objects.all()
    return render(request, 'store/shop.html',{'products':products})

def product(request,slug):
    product = get_object_or_404(Product,slug=slug)
    in_wishlist = Wishlist.objects.filter(Q(product=product)).exists()
    try:
        review = Review.objects.filter(product=product)
        rating = review.aggregate(Avg('rating'))['rating__avg']
    except:
        review=None
        rating=None
    related_products = Product.objects.exclude(id=product.id)
    product_images = ProductImage.objects.filter(product=product)
    return render(request, 'store/product.html',{'product':product,'in_wishlist':in_wishlist,'review':review,'related_products':related_products,'product_images':product_images,'rating':rating})

def cart(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            cart = Cart.objects.create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.subtotal for item in CartItem.objects.filter(cart=cart))
        return render(request, 'store/cart.html',{'cart_items':cart_items,'total_price':total_price})
    return redirect("shop")

def add_to_cart(request,id):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            cart = Cart.objects.create(user=request.user)
        product = Product.objects.get(pk=id)
        
        cart_item = CartItem.objects.filter(cart=cart,product=product)
        if cart_item:
            cart_item = cart_item.first()
            cart_item.quantity += 1
            cart_item.save()
            return redirect("cart")
        cart_item = CartItem.objects.create(cart=cart,product=product)
        return redirect("cart")
    else:
        return redirect("login")

def remove_from_cart(request,id):
    cart = Cart.objects.get(user=request.user)
    product = Product.objects.get(pk=id)
    cart_item = CartItem.objects.get(cart=cart,product=product)
    cart_item.delete()
    return redirect("cart")

def increase_quantity(request,id):
    cart = Cart.objects.get(user=request.user)
    product = Product.objects.get(pk=id)
    cart_item = CartItem.objects.get(cart=cart,product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart")

def decrease_quantity(request,id):
    cart = Cart.objects.get(user=request.user)
    product = Product.objects.get(pk=id)
    cart_item = CartItem.objects.get(cart=cart,product=product)
    cart_item.quantity -= 1
    cart_item.save()
    return redirect("cart")


def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items:
            return redirect("cart")
        total_amount = sum(item.subtotal for item in CartItem.objects.filter(cart=cart))
        products = [item.product.id for item in CartItem.objects.filter(cart=cart)]
        if request.method == "POST":
            domain_name = request.headers['Origin']
            name = request.POST.get('name')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pin = request.POST.get('pin')
            phone = request.POST.get('phone')
            payment_method = request.POST.get('pay-method')
            order = Order.objects.create(customer=user,total_amount=total_amount,name=name,address=address,city=city,state=state,pincode=pin,phone=phone,payment_method=payment_method)
            order.products.add(*products)
            order.save()
            if payment_method == "stripe":
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                            {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                            'name': f"Order Payment for {user}",
                            },
                            'unit_amount': int(total_amount * 100),
                        },
                        'quantity': 1,
                    }
                    ],
                    mode='payment',
                    success_url=domain_name+f"/payment-success/{str(order.order_id)}",
                    cancel_url=domain_name+f"/payment-failed/{str(order.order_id)}"
                )
                order.payment_id=checkout_session.id
                order.save()
                return redirect(checkout_session.url)
            elif payment_method == "razorpay":
                client = razorpay.Client(auth=(config("RZP_KEY"), config("RZP_SECRET")))
                payment = client.order.create({'amount':int(total_amount*100), 'currency':'INR','payment_capture':'1'})
                order.payment_id = payment['id']
                order.save()
                return render(request,'store/checkout.html',{'order':order,'payment':payment,'key':config('RZP_KEY'),'total_amount':total_amount})
        return render(request,'store/checkout.html',{'total_amount':total_amount})
    return redirect("login")

def payment_success(request,id):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        order = get_object_or_404(Order,order_id=id)
        if order.is_paid:
            return redirect("shop")
        if order.payment_id =="stripe":
            charges = stripe.checkout.Session.retrieve(order.payment_id,)
            if charges.payment_status !="paid":
                return redirect("failed")
            order.is_paid = True
            order.status = "success"
            order.save()
        order.is_paid = True
        order.status = "success"
        order.save()
        context = {
            'cart_items': cart_items,
            'id': str(order.order_id),
            'email':order.customer.email,
            'address':f"{order.address}, {order.city}, {order.state}, {order.pincode}",
            'method': str(order.payment_method).upper(),
            'total':sum(item.subtotal for item in cart_items),
            'date':order.created_at
        }
        sendOrderEmail(context)
        cart_items.delete()
        return render(request,'store/payment_success.html')
    return redirect("login")

def payment_failed(request,id):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        order = get_object_or_404(Order, order_id=id)
        if order.is_paid:
            return redirect("shop")
        order.status = "failed"
        order.save()
        cart_items.delete()
        return render(request,'store/payment_failed.html')
    return redirect("login")

def user_dashboard(request):
    orders = Order.objects.filter(customer = request.user)
    return render(request,'store/dashboard.html',{'orders': orders})

def add_to_wishlist(request,id):
    referer = request.META.get('HTTP_REFERER','home')
    try:
        wishlist = Wishlist.objects.get(user=request.user)
    except:
        wishlist = Wishlist.objects.create(user=request.user)
    product_exists = Wishlist.objects.filter(Q(product__id=id)).exists()
    product = Product.objects.get(pk=id)
    if product_exists:
        wishlist.product.remove(product)
    else:
        wishlist.product.add(product)
    return redirect(referer)