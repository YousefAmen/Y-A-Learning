from django.urls import path
import views

urlpatterns = [
    path("cart/", views.get_cart, name="get-cart"),
    path("cart/add/", views.add_cart_item, name="add-cart-item"),
    path("cart/remove/", views.remove_cart_item, name="remove-cart-item"),
]
