from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView, LoginView
from .forms import CustomUserCreationForm
from django.contrib.auth import logout

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('core:home')

def logout_view(request):
    logout(request)
    return redirect('users:login')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})