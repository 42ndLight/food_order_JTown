from django.contrib.auth.backends import BaseBackend
from .models import CustomUser, OTP
from django.utils import timezone

class PasswordBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return None
        try:
            user = CustomUser.objects.get(username=username)
            if user.role in ['admin', 'owner', 'staff'] and user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

class OTPBackend(BaseBackend):
    def authenticate(self, request, phone_no=None, otp_code=None):
        if not phone_no or not otp_code:
            return None
        try:
            user = CustomUser.objects.get(phone_no=phone_no)
            if user.role != 'customer':
                return None  # Only customers use OTP
            otp = OTP.objects.filter(user=user, code=otp_code).first()
            if otp and otp.is_valid():
                otp.delete()  # One-time use
                return user
        except CustomUser.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None