from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import logout
from .forms import StaffLoginForm, SendOTPForm, VerifyOTPForm, CustomUserCreationForm
from django.conf import settings
from .models import OTP, CustomUser
from django.views.generic import FormView
import africastalking


# Create your views here.
'''africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms = africastalking.SMS'''

from django.conf import settings

def send_otp_sms(phone_no, code):
    message = f"Your JTown Burgers OTP is {code}. Valid for 30 minutes."
    if settings.DEBUG:
        print(f"OTP for {phone_no}: {code}")  # Log OTP to console for testing
        return
    try:
        sms.send(message, [phone_no])
    except Exception as e:
        print(f"SMS error: {e}")



class StaffLoginView(LoginView):
    template_name = 'users/staff_login.html'
    form_class = StaffLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.get_user()
        if user.role not in ['admin', 'owner', 'staff']:
            return self.form_invalid(form)
        return super().form_valid(form)

class CustomerSendOTPView(FormView):
    template_name = 'users/customer_send_otp.html'
    form_class = SendOTPForm
    success_url = reverse_lazy('users:customer_verify_otp')

    def form_valid(self, form):
        phone_no = form.cleaned_data['phone_no']
        try:
            user = CustomUser.objects.get_or_create_customer(phone_no)
            otp = OTP.generate_otp(user)
            self.request.session['otp_user_id'] = user.id
            return super().form_valid(form)
        except CustomUser.DoesNotExist:
            form.add_error('phone_no', 'No Customer Account Found With this phone no')
            return super().form_invalid(form)



class CustomerVerifyOTPView(FormView):
    template_name = 'users/customer_verify_otp.html'
    form_class = VerifyOTPForm
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        otp_code = form.cleaned_data['otp_code']
        user_id = self.request.session.get('otp_user_id')
        if not user_id:
            return redirect('users:customer_send_otp')
        user = CustomUser.objects.get(id=user_id)
        if OTP.objects.filter(user=user, code=otp_code, expires_at__gt=timezone.now()).exists():
            OTP.objects.filter(user=user).delete()
            login(self.request, user, backend='users.backend.OTPBackend')
            return super().form_valid(form)
        form.add_error('otp_code', 'Invalid or Expired OTP.')
        return self.form_invalid(form)



def logout_view(request):
    logout(request)
    return redirect('core:home')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if user.role == 'customer':  # Safety check, though form excludes it
                form.add_error('role', 'Customers cannot be registered this way.')
                return render(request, 'users/register.html', {'form': form})
            form.save()
            return redirect('users:staff_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})