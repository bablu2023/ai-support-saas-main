from django.urls import path
from .views import create_payment, verify_payment

urlpatterns = [
    path("create-payment/", create_payment),
    path("verify-payment/", verify_payment),
]
