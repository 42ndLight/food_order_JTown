from django.urls import path
from .views import MpesaPaymentView, mpesa_callback

urlpatterns = [
	#path('pay/push/<int:phone_number>', MpesaPaymentView.as_view(), name='mpesapush'),
	path('callback/contributions/', mpesa_callback, name='mpesa-callback'),
        
]
