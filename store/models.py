from django.db import models
import uuid
from accounts.models import User
from django.template.defaultfilters import slugify


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

class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    customer = models.ForeignKey(User,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,related_name="order_products")
    total_amount = models.DecimalField(max_digits=6,decimal_places=2)
    shipping_address = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=15,blank=True,null=True)      
    payment_id = models.CharField(max_length=255,blank=True,null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order_id)
    
class Review(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    rating = models.IntegerField()
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