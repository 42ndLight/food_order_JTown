from django.contrib import admin
from .models import Category, MenuItem

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'image', 'category_id', 'available')
    search_fields = ('name', 'description', 'category_id', 'available')

admin.site.register(MenuItem, MenuItemAdmin)

admin.site.register(Category, CategoryAdmin)