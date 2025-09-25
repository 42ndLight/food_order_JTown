from django.db import models
from orders.models import Order
from django.conf import settings


class MpesaTransaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='mpesa_transaction')
    checkout_request_id = models.CharField(max_length=100, unique=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_date = models.DateTimeField(auto_now_add=True)
    callback_data = models.JSONField(blank=True, null=True)  # Store full callback response

    def __str__(self):
        return f"Transaction for Order {self.order.id} - {self.status}"