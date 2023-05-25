from django.contrib import admin
from .models import Category,Product,Order,Review,Wishlist,Cart,CartItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)