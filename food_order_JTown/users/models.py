from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
        ('customer', 'Customer'),
    ]
    

    phone_no = models.CharField(max_length=12, unique=True, help_text="eg., 254712345678")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    loyalty_points = models.IntegerField(default=0)



    def __str__(self):
        return f"{self.username} - {self.role}"
    
    class Meta:
        permissions = [
            ("can_manage_shop", "Can manage shop dashboard and menu"),
            ("can_view_dashboard", "Can view shop dashboard"),
        ]