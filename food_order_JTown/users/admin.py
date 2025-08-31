from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'date_joined', 'last_login', 'phone_no', 'role')
    search_fields = ('username', 'email', 'phone_no', 'role')

admin.site.register(User, UserAdmin)
# Register your models here.
