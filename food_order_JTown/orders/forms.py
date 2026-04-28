from django import forms
from core.models import MenuItem
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'address', 'building_name', 'street', 'latitude', 'longitude', 'delivery_fee']
        widgets = {
            'user': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'delivery_fee': forms.HiddenInput(),
            'address': forms.TextInput(attrs={'placeholder': 'Address', 'class': 'form-control'}),
            'building_name': forms.TextInput(attrs={'placeholder': 'Building Name', 'class': 'form-control'}),
            'street': forms.TextInput(attrs={'placeholder': 'Street', 'class': 'form-control'}),
        }

class OrderItemForm(forms.Form):
	menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.filter(available=True))
	quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class':
		'form-control', 'min':'1'}))

	def clean_quantity(self):
		quantity= self.cleaned_data['quantity']
		if quantity <= 0:
			raise forms.ValidationError("Quantity must be greater than 0.")
		return quantity
