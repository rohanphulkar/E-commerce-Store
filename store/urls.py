from django.urls import path
from . import views
urlpatterns = [
    path("",views.shop,name="shop"),
    path("product/<slug>/",views.product,name="product"),
    path("cart/",views.cart,name="cart"),
    path("add-to-cart/<id>/",views.add_to_cart,name="add_to_cart"),
    path("remove-from-cart/<id>/",views.remove_from_cart,name="remove_from_cart"),
    path("increase-quantity/<id>/",views.increase_quantity,name="increase_quantity"),
    path("decrease-quantity/<id>/",views.decrease_quantity,name="decrease_quantity"),
    path("checkout/",views.checkout,name="checkout"),
    path("payment-success/<id>/",views.payment_success,name="payment_success"),
    path("payment-failed/<id>/",views.payment_failed,name="payment_failed"),
    path("dashboard/",views.user_dashboard,name="dashboard")
]
