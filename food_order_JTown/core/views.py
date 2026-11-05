from django.views.generic import TemplateView, ListView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Category, MenuItem, GalleryImage, ContactMessage
from .forms import ContactForm

# Create your views here.
class HomeView(TemplateView):
    template_name = 'core/home.html'


def customer_dashboard(request):   
    return render(request, 'core/customer_dashboard.html', {'user': request.user})

@login_required
def staff_dashboard(request):
    if request.user.role not in ['admin', 'staff', 'owner']:
        return HttpResponseForbidden("Access denied.")
    return render(request, 'core/staff_dashboard.html', {'user': request.user})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            messages.success(
                request,
                f"Thank you, {contact_msg.name}! Your message has been received. Our team will get back to you shortly."
            )
            return redirect('core:contact')
        else:
            messages.error(request, "Please correct the errors below and try submitting again.")
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


def about(request):
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order', '-created_at')
    return render(request, 'core/about.html', {'gallery_images': gallery_images})


class MenuView(ListView):
    model = MenuItem
    template_name = 'core/menu.html'
    context_object_name = 'menu_items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = list(Category.objects.all())
        items_by_category = [(c, MenuItem.objects.filter(category_id=c, available=True)) for c in categories]
        context['categories'] = categories
        context['items_by_category'] = items_by_category
        return context

