from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import logout, login, authenticate
from .forms import StaffLoginForm, SendOTPForm, VerifyOTPForm, CustomUserCreationForm
from django.conf import settings
from .models import OTP, CustomUser
from django.views.generic import FormView
from django.http import HttpResponseForbidden, HttpResponseRedirect
#import africastalking
from django.utils import timezone
import uuid
from django.views.decorators.http import require_http_methods

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

    def get_success_url(self):
        user = self.request.user
        if user.role in ['admin', 'staff', 'owner']:
            return reverse_lazy('core:staff_dashboard')
        return reverse_lazy('core:home')

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
            self.request.session['otp_token'] = str(uuid.uuid4())  # Generate and store token
            if settings.DEBUG:
                self.request.session['debug_otp'] = otp.code  # Optional for testing
            send_otp_sms(phone_no, otp.code)  # Send OTP (or log in debug mode)
            self.success_url = reverse_lazy('users:customer_verify_otp') + f'?token={self.request.session["otp_token"]}'
            return super().form_valid(form)
        except CustomUser.DoesNotExist:
            form.add_error('phone_no', 'No Customer Account Found With this phone no')
            return super().form_invalid(form)



import logging

# Set up logging
logger = logging.getLogger(__name__)

class CustomerVerifyOTPView(FormView):
    template_name = 'users/customer_verify_otp.html'
    form_class = VerifyOTPForm

    def get_success_url(self):
        return reverse_lazy('core:customer_dashboard')

    def get(self, request, *args, **kwargs):
        url_token = request.GET.get('token')
        session_token = request.session.get('otp_token')
        if not url_token or not session_token or url_token != session_token:
            return HttpResponseForbidden("Invalid access to OTP verification.")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        url_token = self.request.GET.get('token')
        session_token = self.request.session.get('otp_token')
        if not url_token or not session_token or url_token != session_token:
            return HttpResponseForbidden("Invalid access to OTP verification.")

        otp_code = form.cleaned_data['otp_code']
        user_id = self.request.session.get('otp_user_id')
        if not user_id:
            return redirect('users:customer_send_otp')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            form.add_error(None, 'User not found. Please request a new OTP.')
            return self.form_invalid(form)

        logger.debug(f"Attempting authenticate with user={user.id}, otp_code={otp_code}")
        user = authenticate(request=self.request, user=user, otp_code=otp_code)
        if user is not None:
            logger.debug(f"Authentication successful for user={user.id}")
            login(self.request, user, backend='users.backend.OTPBackend')
            # Clear session keys
            if 'otp_user_id' in self.request.session:
                del self.request.session['otp_user_id']
            if 'otp_token' in self.request.session:
                del self.request.session['otp_token']
            if 'debug_otp' in self.request.session:
                del self.request.session['debug_otp']
            logger.debug(f"Redirecting to {self.get_success_url()}")
            return HttpResponseRedirect(self.get_success_url())
        else:
            logger.debug(f"Authentication failed for user={user.id}, otp_code={otp_code}")
            form.add_error('otp_code', 'Invalid or expired OTP.')
            return self.form_invalid(form)

@require_http_methods(["GET"])            
def logout_view(request):
    logout(request)
    return redirect('core:home')

@require_http_methods(["POST"])
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'customer':  # Safety check, though form excludes it
                form.add_error('role', 'Customers cannot be registered this way.')
                return render(request, 'users/register.html', {'form': form})
            
            return redirect('users:staff_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})