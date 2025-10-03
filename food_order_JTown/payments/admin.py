from django.contrib import admin
from .models import MpesaTransaction

# Register your models here.
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'checkout_request_id', 'mpesa_receipt_number', 'amount', 'status', 'transaction_date')
    search_fields = ('order__id', 'transaction_id', 'mpesa_receipt_number')

admin.site.register(MpesaTransaction, MpesaTransactionAdmin)