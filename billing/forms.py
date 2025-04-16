from django import forms
from decimal import Decimal, InvalidOperation
from .models import Billing,Payment

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if isinstance(amount, str):
            try:
                return Decimal(amount)
            except InvalidOperation:
                raise forms.ValidationError("Invalid amount. Please enter a valid number.")
        return amount



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method','dr_account']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount or amount <= 0:
            raise forms.ValidationError("Amount must be a positive value.")
        return amount
