from django.urls import path
from .views import MpesaPaymentView, mpesa_callback, check_payment_status

app_name = 'payments'   

urlpatterns = [
    path('pay/push/', MpesaPaymentView.as_view(), name='mpesa-push'),
    path('pay/push/alt/', MpesaPaymentView.as_view(), name='mpesapush'),
    path('status/', check_payment_status, name='check-payment-status'),
    path('callback/contributions/', mpesa_callback, name='mpesa-callback'),
]
