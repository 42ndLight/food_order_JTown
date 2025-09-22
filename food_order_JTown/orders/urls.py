from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('checkout/', views.OrderCreateView.as_view(), name='order_create'),
    path('order/success/', views.OrderSuccessView.as_view(), name='order_success'),
]