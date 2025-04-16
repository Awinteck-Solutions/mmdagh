from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['billing', 'amount', 'method', 'payment_date']

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment amount'}),
            'method': forms.Select(attrs={'class': 'form-control'}),
        }

class GhanaCardForm(forms.Form):
    ghana_card_number = forms.CharField(
        label='Ghana Card Number',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Ghana Card number'})
    )