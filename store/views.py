from django.shortcuts import render,redirect
from .models import Category,Product,Order,Review,Wishlist,Cart,CartItem
from django.shortcuts import get_object_or_404
import stripe
from decouple import config
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
    return render(request, 'store/product.html',{'product':product})

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
        if request.method == "POST":
            domain_name = request.headers['Origin']
            shipping_address = request.POST.get('address')
            phone = request.POST.get('phone')
            total_amount = sum(item.product.price for item in CartItem.objects.filter(cart=cart))
            products = [item.product.id for item in CartItem.objects.filter(cart=cart)]
            order = Order.objects.create(customer=user,total_amount=total_amount,shipping_address=shipping_address,phone=phone)
            order.products.add(*products)
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
            cart_items.delete()
            return redirect(checkout_session.url)
        return render(request,'store/checkout.html')
    return redirect("login")

def payment_success(request,id):
    order = get_object_or_404(Order,order_id=id)
    if order.is_paid:
        return redirect("shop")
    charges = stripe.checkout.Session.retrieve(order.payment_id,)
    if charges.payment_status !="paid":
        return redirect("failed")
    order.is_paid = True
    order.save()
    return render(request,'store/payment_success.html')

def payment_failed(request,id):
    order = get_object_or_404(Order, order_id=id)
    if order.is_paid:
        return redirect("shop")
    return render(request,'store/payment_failed.html')

def user_dashboard(request):
    orders = Order.objects.filter(customer = request.user)
    return render(request,'store/dashboard.html',{'orders': orders})