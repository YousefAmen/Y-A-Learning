from django.urls import path

from .views import add_to_cart, cart_detail, remove_from_cart

app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/', add_to_cart, name='add-to-cart'),
    path('remove/', remove_from_cart, name='remove-from-cart'), 
]