from decimal import Decimal, ROUND_HALF_UP
from django import forms
from core.models import MenuItem
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    delivery_fee = forms.DecimalField(
        required=False,
        initial=Decimal('0.00'),
        widget=forms.HiddenInput()
    )
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Order
        fields = ['user', 'address', 'building_name', 'street', 'latitude', 'longitude', 'delivery_fee']
        widgets = {
            'user': forms.HiddenInput(),
            'address': forms.TextInput(attrs={'placeholder': 'Address, room, or landmark', 'class': 'form-control'}),
            'building_name': forms.TextInput(attrs={'placeholder': 'Building Name', 'class': 'form-control'}),
            'street': forms.TextInput(attrs={'placeholder': 'Street', 'class': 'form-control'}),
        }

    def clean_delivery_fee(self):
        fee = self.cleaned_data.get('delivery_fee')
        if fee is None or fee == '':
            return Decimal('0.00')
        return fee
        
    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is not None:
            # Rounds to exactly 6 decimal places
            return lat.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        return lat

    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng is not None:
            # Rounds to exactly 6 decimal places
            return lng.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        return lng

class OrderItemForm(forms.Form):
	menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.filter(available=True))
	quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class':
		'form-control', 'min':'1'}))

	def clean_quantity(self):
		quantity= self.cleaned_data['quantity']
		if quantity <= 0:
			raise forms.ValidationError("Quantity must be greater than 0.")
		return quantity
