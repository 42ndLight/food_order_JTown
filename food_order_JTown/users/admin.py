from django.contrib import admin
from .models import CustomUser

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'last_login', 'phone_no', 'role')
    search_fields = ('username', 'email', 'phone_no', 'role')

admin.site.register(CustomUser, UserAdmin)
# Register your models here.
