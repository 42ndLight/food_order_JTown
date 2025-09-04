from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta
from django.utils import timezone
import string
import secrets

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, phone_no=None,password=None, role='customer', **extra_fields):
        if role == 'customer':
            if not phone_no:
                raise ValueError('Customers must have a phone number')
            user = self.model(phone_no=phone_no, role=role, **extra_fields)
            user.set_unusable_password()
        else:
            if not username:
                raise ValueError('Staff/Owner mmmust have username')
            user = self.model(username=username,phone_no=phone_no, role=role, **extra_fields)
            if password:
                user.set_password(password)
        user.save(using=self._db)
        return user

    def get_or_create_customer(self, phone_no):
        try:
            return self.get(phone_no=phone_no, role='customer')
        except CustomUser.DoesNotExist:
            return self.create_user(phone_no=phone_no, role='customer')
            

    def create_superuser(self, username, password, phone_no, **extra_fields):
        extra_fields.update(phone_no=phone_no)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(username, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
        ('customer', 'Customer'),
    ]
    
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_no = models.CharField(max_length=12, unique=True, help_text="eg., 254712345678")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    loyalty_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role', 'phone_no`']



    def __str__(self):
        return f"{self.username} - {self.role}"
    
    class Meta:
        permissions = [
            ("can_manage_shop", "Can manage shop dashboard and menu"),
            ("can_view_dashboard", "Can view shop dashboard"),
        ]

class OTP(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at


    @classmethod
    def generate_otp(cls, user, alphanumeric = True, length=6):
        if alphanumeric:
        # Use uppercase letters and digits for better readability
            alphabet = string.ascii_uppercase + string.digits
        # Remove potentially confusing characters
            alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        else:
        # Numeric only
            alphabet = string.digits
    
    # Generate secure random code
        code = ''.join(secrets.choice(alphabet) for _ in range(length))        
        expires_at = timezone.now() + timedelta(minutes=30)
        return cls.objects.create(user=user, code=code, expires_at=expires_at)