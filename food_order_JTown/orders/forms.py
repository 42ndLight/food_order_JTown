#forms.py

from django import forms
from core.models import MenuItem
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['user']
		widgets = {
			'user': forms.HiddenInput(),
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
			