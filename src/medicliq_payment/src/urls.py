from django.urls import path
from . import views

app_name = "medicliq_payment"

urlpatterns = [
    path('cart2/', views.cart2, name='cart2'),
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment-status/', views.payment_status, name='payment_status'),
    path('success/', views.payment_success, name='payment_success'),
    path("log-cart-data/", views.log_cart_data, name="log_cart_data"),

]