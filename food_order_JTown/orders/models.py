from django.db import models
from core.models import MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Order(models.Model):
	STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	status= models.CharField(max_length=20, choices= STATUS_CHOICES, default='Pending')
	created_at = models.DateField(auto_now_add=True)

	def __str__(self):
		return f"Order {self.id} by {self.user or 'Guest'}"

class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	price = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"{self.quantity} x {self.menu_item.name}"


