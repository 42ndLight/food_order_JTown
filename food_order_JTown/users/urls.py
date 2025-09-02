from django.urls import path
from .views import StaffLoginView, CustomerSendOTPView, CustomerVerifyOTPView, logout_view, register

app_name = 'users'
urlpatterns = [
    path('staff/login/', StaffLoginView.as_view(), name='staff_login'),
    path('customer/login/', CustomerSendOTPView.as_view(), name='customer_send_otp'),
    path('customer/verify/', CustomerVerifyOTPView.as_view(), name='customer_verify_otp'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register')
]
