from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods


# Create your views here.
class HomeView(TemplateView):
    template_name = 'core/home.html'


@require_http_methods(["GET"])
def customer_dashboard(request):   
    return render(request, 'core/customer_dashboard.html', {'user': request.user})

@login_required
@require_http_methods(["GET"])
def staff_dashboard(request):
    if request.user.role not in ['admin', 'staff', 'owner']:
        return HttpResponseForbidden("Access denied.")
    return render(request, 'core/staff_dashboard.html', {'user': request.user})

@require_http_methods(["GET"])
def menu(request):
    return render(request, 'core/menu.html')

@require_http_methods(["GET"])
def contact(request):
    return render(request, 'core/contact.html')

@require_http_methods(["GET"])
def about(request):
    return render(request, 'core/about.html')