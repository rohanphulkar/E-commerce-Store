from django.db import models
import uuid
from accounts.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator,MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="store/products/")
    description = models.TextField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products/images")

    def __str__(self):
        return self.product.name

class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    customer = models.ForeignKey(User,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,related_name="order_products")
    total_amount = models.DecimalField(max_digits=6,decimal_places=2)
    name = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255,default="")
    city = models.CharField(max_length=255,default="")
    state = models.CharField(max_length=255,default="")
    pincode = models.CharField(max_length=6,default="")
    phone = models.CharField(max_length=15,blank=True,null=True)
    payment_method = models.CharField(max_length=10,choices=(("razorpay",'razorpay'),("stripe",'stripe')),default="")   
    payment_id = models.CharField(max_length=255,blank=True,null=True)
    status = models.CharField(max_length=50,choices=(("pending",'pending'),("failed",'failed'),("success",'success')),default="pending")
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order_id)
    
class Review(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.product.name} by {self.user.email}"

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ManyToManyField(Product,related_name="wishlist_product")

    def __str__(self):
        return f"Wishlist of {self.user.email}"
    
class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=8,decimal_places=2,default=0)

    def __str__(self):
        return self.product.name
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)