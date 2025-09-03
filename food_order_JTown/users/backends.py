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
    def authenticate(self, request, user=None, otp_code=None, **kwargs):
        if user is None or otp_code is None:
            return None
        try:
            otp = OTP.objects.filter(user=user, code=otp_code).first()
            if otp and otp.is_valid():
                return user
            return None
        except OTP.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None