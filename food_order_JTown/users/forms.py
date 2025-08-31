from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    phone_no = forms.CharField(max_length=12, help_text="eg., 254712345678")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone_no', 'role')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_no = self.cleaned_data['phone_no']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user 