from django.urls import path
from .views import HomeView, MenuView
from . import views

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),

]
