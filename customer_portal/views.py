from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Billing, Payment  # Adjust based on your models
from .forms import PaymentForm  # Create this form for handling payments
from accounts.models import DataCapture  # Import the DataCapture model
from .forms import GhanaCardForm  # Form to accept Ghana Card input

def dashboard(request):
    """
    Dashboard to display user info and a summary of bills based on Ghana Card.
    """
    bills = None
    if request.method == 'POST':
        form = GhanaCardForm(request.POST)
        if form.is_valid():
            ghana_card_number = form.cleaned_data['ghana_card_number']
            try:
                # Fetch bills associated with the Ghana Card number
                bills = Billing.objects.filter(ghana_card=ghana_card_number)
                if not bills.exists():
                    messages.info(request, "No bills found for the provided Ghana Card number.")
            except Billing.DoesNotExist:
                messages.error(request, "No bills found for the provided Ghana Card number.")
    else:
        form = GhanaCardForm()
    
    return render(request, 'customer_portal/dashboard.html', {'form': form, 'bills': bills})


def view_bills(request):
    """
    Display all bills for the logged-in user.
    """
    bills = Billing.objects.filter(account=request.user).order_by('-created_at')
    return render(request, 'customer_portal/bills.html', {'bills': bills})

def view_bill_details(request, billing_id):
    """
    Show details for a specific bill.
    """
    bill = get_object_or_404(Billing, id=billing_id, account=request.user)
    return render(request, 'customer_portal/bill_details.html', {'bill': bill})

def pay_bill(request, billing_id):
    """
    Handle payment for a specific bill.
    """
    bill = get_object_or_404(Billing, id=billing_id, account=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.billing = bill
            payment.save()
            messages.success(request, "Payment successful!")
            return redirect('view_bills')
    else:
        form = PaymentForm()
    return render(request, 'customer_portal/pay_bill.html', {'bill': bill, 'form': form})
