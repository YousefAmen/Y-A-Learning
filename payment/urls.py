from django.urls import path
from .views import checkout, payment_success, payment_failed

app_name = "payment"

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("success-payment/", payment_success, name="payment-success"),
    path("payment-failed/", payment_failed, name="payment-failed"),
]
