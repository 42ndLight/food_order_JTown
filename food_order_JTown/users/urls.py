from django.urls import path
from .views import CustomLoginView, logout_view, register

app_name = 'users'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register')
]
