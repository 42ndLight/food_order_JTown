from django.contrib import admin
from .models import OrderItem, Order
# Register your models here.

class OrderItemAdmin(admin.ModelAdmin):
	list_display= ('id','order','menu_item','quantity','price')
	search_fields = ('order','menu_item','quantity','price')

class OrderAdmin(admin.ModelAdmin):
	list_display= ('user','status','total_price','created_at')
	search_fields = ('user','status','total_price','created_at')

admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
