#signals.py
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Order

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    order = instance.order
    subtotal = sum(item.price * item.quantity for item in order.items.all())
    delivery_fee = order.delivery_fee or Decimal('0.00')
    order.total_price = subtotal + Decimal(str(delivery_fee))
    order.save()