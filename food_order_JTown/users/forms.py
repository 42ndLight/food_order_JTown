from django import forms 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    phone_no = forms.CharField(max_length=12, help_text="eg., 254712345678")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('phone_no', 'role')
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'customer':
            raise forms.ValidationError("Customers cannot be registered this way. Use phone-based login.")
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_no = self.cleaned_data['phone_no']
        user.role = self.cleaned_data['role']
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user 


class StaffLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class SendOTPForm(forms.Form):
    phone_no = forms.CharField(
        max_length = 12,
        help_text="Enter your phone: +2547xxxxxxxx"
        )

class VerifyOTPForm(forms.Form):
    otp_code = forms.CharField(max_length=6, help_text="Kindly Enter the OTP code sent")