from django.contrib import admin
from .models import Category,Product,Order,Review,Wishlist,Cart,CartItem,ProductImage

admin.site.register(Category)

class ProductImageInline(admin.TabularInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product,ProductAdmin)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)