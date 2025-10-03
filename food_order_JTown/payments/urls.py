from django.urls import path
from .views import MpesaPaymentView, mpesa_callback

app_name='payments'   

urlpatterns = [
	path('pay/push/', MpesaPaymentView.as_view(), name='mpesapush'),
	path('callback/contributions/', mpesa_callback, name='mpesa-callback'),
        
]
