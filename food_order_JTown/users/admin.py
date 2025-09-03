from django.contrib import admin
from .models import CustomUser, OTP

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'last_login', 'phone_no', 'role')
    search_fields = ('username', 'email', 'phone_no', 'role')


class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at')
    search_fields = ('user__phone_no', 'code')

admin.site.register(CustomUser, UserAdmin)
admin.site.register(OTP, OTPAdmin)

