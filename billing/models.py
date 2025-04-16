from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.db.models import Sum
#from account.models import DataCapture
from django.db import transaction
import logging
from decimal import Decimal
from django.contrib.auth.models import User
from accounts.models import DataCapture ,MMDA # Import the DataCapture model
from datetime import datetime
from django.db import models, transaction  # Ensure these models are imported
from django.utils.timezone import now


# Set up logging
logger = logging.getLogger(__name__)

CATEGORY_CHOICES = [
    ('INDV', 'Individual'),
    ('RES', 'Residential'),
    ('EDU', 'Education'),
    ('FIS', 'Financial Institution'),
    ('REG', 'Religious'),
    ('BUS', 'Business/Manufacturing'),
    ('GOV', 'Government Agencies')

]


class CustomerStatement(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('bill', 'Bill'),
        ('payment', 'Payment'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    customer_name = models.CharField(max_length=255)
    dr_account = models.ForeignKey(DataCapture, on_delete=models.CASCADE, related_name='debits')
    cr_account = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name='credits')
    cr_account_name = models.CharField(max_length=255)
    year_bill = models.PositiveIntegerField()
    date_generated = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)  # Payment method for payments, auto for bills

    def __str__(self):
        return f"{self.transaction_type} - {self.customer_name} - {self.amount}"

class Billing(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partly_paid', 'Partly Paid'),
        ('paid', 'Paid'),
    ]

    account = models.ForeignKey(DataCapture, on_delete=models.CASCADE, related_name="bills")
    accounting_year = models.PositiveIntegerField()  # Year of the bill
    brought_forward = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Previous year's unpaid balance
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="bills")  # MMDA Reference

    name_mmda = models.CharField(max_length=255)
    ghana_card = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    gps_address = models.CharField(max_length=255)
    bill_date = models.DateTimeField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Current year's bill
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # B/F + Current year's bill
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total payments
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total due - Total paid
    rooms = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_option = models.CharField(max_length=50, choices=[('full', 'Full'), ('installments', 'Installments')])
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.account} - Billing ID: {self.id}"

    def save(self, *args, **kwargs):
        # Check if the instance is being created (not updated)
        if not self.pk:  # This means the instance is new
            super().save(*args, **kwargs)  # Save the billing instance first

            # Create a customer statement entry for the bill
            CustomerStatement.objects.create(
                transaction_type='bill',
                customer_name=self.recipient_name,
                dr_account=self.account,
                cr_account=self.mmda,
                cr_account_name=self.mmda.name,
                year_bill=self.accounting_year,
                amount=self.total_due,
                method='auto'  # Assuming bills are auto-generated
            )
        else:
            # If updating, just save the instance
            super().save(*args, **kwargs)



    def get_category_display(self):
        return self.account.category  # Fetch category from DataCapture


    @property
    def previous_year(self):
        return datetime.now().year - 1  # Always returns the previous year dynamically

    def __str__(self):
        return f"Billing {self.id} - Previous Year: {self.previous_year}"


    @staticmethod
    def move_to_next_year(accounting_year):
        """
        Move unpaid balances to brought forward for the next year.
        """
        current_bills = Billing.objects.filter(accounting_year=accounting_year)
        next_year = accounting_year + 1

        for bill in current_bills:
            if bill.closing_balance > 0:
                logger.info(f"Moving balance for {bill.account} to {next_year}.")
                next_year_bill, created = Billing.objects.get_or_create(
                    account=bill.account,
                    accounting_year=next_year,
                    defaults={
                        'brought_forward': bill.closing_balance,
                        'name_mmda': bill.name_mmda,
                        'ghana_card': bill.ghana_card,
                        'recipient_name': bill.recipient_name,
                        'address': bill.address,
                        'contact_number': bill.contact_number,
                        'gps_address': bill.gps_address,
                        'rooms': bill.rooms,
                    }
                )
                if not created:
                    next_year_bill.brought_forward += bill.closing_balance
                    next_year_bill.save(update_fields=['brought_forward'])


    @property

    def total_paid_calculated(self):

        return Decimal(self.payments.aggregate(total=Sum('amount'))['total'] or 0)


    def update_total_paid(self):

        self.total_paid = self.total_paid_calculated

        self.save(update_fields=['total_paid'])


    def calculate_closing_balance(self):

        """Calculate the closing balance and update payment status."""

        self.closing_balance = self.total_due - self.total_paid  # Both are now Decimal

        self.payment_status = (

            'paid' if self.closing_balance <= 0 else

            'partly_paid' if self.total_paid > 0 else

            'unpaid'

        )

        self.save(update_fields=['closing_balance', 'payment_status'])


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._updating_payment_status = False  # Initialize the flag in the constructor

    @property

    def amount_due(self):

        """Calculate amount due dynamically."""

        return Decimal(self.amount) - self.total_paid  # Convert amount to Decimal

    def update_payment_status(self):
        """Updates the payment status based on the total amount paid."""
        if getattr(self, '_updating_payment_status', False):
            return  # Prevent recursion

        # Set the flag to avoid recursion
        self._updating_payment_status = True

        # Use the amount_due property directly
        if self.amount_due <= 0:
            self.payment_status = 'paid'
            self.is_paid = True
        elif self.total_paid > 0:
            self.payment_status = 'partly_paid'
            self.is_paid = False
        else:
            self.payment_status = 'unpaid'
            self.is_paid = False

        # Save the object without triggering recursion for the payment status update
        super().save()

        # Reset the flag
        self._updating_payment_status = False


def save(self, *args, **kwargs):
    # Ensure the amount is calculated during save
    if not self.pk:  # If the instance is being created
        try:
            # Fetch the rate for the selected category
            rate = Rate.objects.get(category=self.category)
            if self.rooms > 0:
                self.amount = rate.rate * self.rooms
            else:
                raise ValueError("Rooms must be a positive integer.")
        except Rate.DoesNotExist:
            self.amount = 0.0  # Default to 0 if no rate exists
        except ValueError as e:
            raise ValueError(f"Invalid data: {e}")

    # Update dependent fields
    self.amount_due = self.amount - self.total_paid
    self.amount_left = max(self.amount_due, 0.0)

    # Save the instance
    super().save(*args, **kwargs)

    # Update related Billing's total_paid dynamically if needed
    self.billing.update_total_paid()




    def __str__(self):
        return f"Billing for {self.recipient_name} ({self.category}) - GHS {self.amount}"

    class Meta:
        verbose_name = "Billing"
        verbose_name_plural = "Billings"
        ordering = ['-bill_date']


@receiver(post_save, sender=DataCapture)
def update_billing_on_datacapture_change(sender, instance, **kwargs):
    try:
        billing, created = Billing.objects.get_or_create(account=instance)

        # Update existing billing
        billing.category = instance.category
        billing.rooms = instance.rooms

        try:
            rate = Rate.objects.get(category=self.category)
            billing.amount = rate.rate * self.rooms
        except Rate.DoesNotExist:
            logger.error(f"Rate does not exist for category {instance.category}")
            billing.amount = 0.0

        # Save the billing instance to ensure it has a primary key
        billing.save()

        # Update payment status after saving
        billing.update_payment_status()

    except Exception as e:
        logger.error(f"Error in updating billing for DataCapture {instance.id}: {str(e)}")

class Rate(models.Model):
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES, unique=True)
    rate = models.FloatField()

    def __str__(self):
        return f"{self.get_category_display()} - {self.rate} GHS"
    
    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"


class Payment(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name="payments")
    amount = models.FloatField(default=0.0)
    payment_date = models.DateTimeField(auto_now_add=True)
    # Define payment method choices
    METHOD_CASH = 'cash'
    METHOD_MOBILE = 'mobile_money'
    METHOD_BANK = 'bank_transfer'
    
    METHOD_CHOICES = [
        (METHOD_CASH, 'Cash'),
        (METHOD_MOBILE, 'Mobile Money'),
        (METHOD_BANK, 'Bank Transfer'),
    ]

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default=METHOD_CASH
    )
    #dr_account = models.ForeignKey(account, related_name='debit_payments')
    #cr_account = models.ForeignKey(Account, related_name='credit_payments')
    transaction_id = models.CharField(max_length=20)
    dr_account = models.CharField(max_length=20)  # 

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)  # Save the payment first

            # Update the associated billing
            self.billing.update_total_paid()  # Call the method to update total_paid
            self.billing.calculate_closing_balance()  # Update the closing balance

            # Create a customer statement entry for the payment
            CustomerStatement.objects.create(
                transaction_type='payment',
                payment_id=self.generate_payment_id(),  # Implement this method to generate the ID
                customer_name=self.billing.recipient_name,
                dr_account=self.billing.account,
                cr_account=self.billing.mmda,
                cr_account_name=self.billing.mmda.name,
                year_bill=self.billing.accounting_year,
                amount=self.amount,
                method=self.method
            )

    def generate_payment_id(self):
        # Implement logic to generate a unique payment ID
        from datetime import datetime
        now = datetime.now()
        sequence = Payment.objects.filter(payment_date__date=now.date()).count() + 1
        return f"P{now.strftime('%Y%m%d%H%M%S')}{str(sequence).zfill(3)}"

    def __str__(self):
        return f"Payment of {self.amount} for {self.billing.recipient_name} on {self.payment_date}"

    def generate_payment_id(self):
        # Generate a unique payment ID based on the current time and sequence
        from datetime import datetime
        now = datetime.now()
        sequence = Payment.objects.filter(payment_date__date=now.date()).count() + 1
        return f"P{now.strftime('%Y%m%d%H%M%S')}{str(sequence).zfill(3)}"



class RevenueTarget(models.Model):
    year = models.PositiveIntegerField()
    target = models.FloatField(default=0.0)

    def __str__(self):
        return f"Target for {self.year}: GHS {self.target}"

# billing/models.py
class MonthlyRevenue(models.Model):
    # fields and methods for MonthlyRevenue
    pass

# billing/models.py
class PaymentCategory(models.Model):
    # fields and methods for MonthlyRevenue
    pass

# billing/models.py
class UnpaidBills(models.Model):
    # fields and methods for MonthlyRevenue
    pass

# billing/models.py
class PaymentHistory(models.Model):
    # fields and methods for MonthlyRevenue
    pass

# billing/models.py
class PaymentByMethod(models.Model):
    # fields and methods for MonthlyRevenue
    pass

# billing/models.py
class TopPayments(models.Model):
    # fields and methods for MonthlyRevenue
    pass

class PaymentMethodVolume(models.Model):
    method = models.CharField(max_length=50)
    volume = models.IntegerField()

    def __str__(self):
        return f"{self.method}: {self.volume}"


class AccumulatedOwing(models.Model):
    account = models.ForeignKey('accounts.DataCapture', on_delete=models.CASCADE, related_name='accumulated_owings')
    year = models.IntegerField()  # Accounting year
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount owed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account} - {self.year} - {self.amount}"


def changelist_view(self, request, extra_context=None):
    extra_context = extra_context or {}

    # Payment Trends Over Time (Monthly)
    payment_trends = (
        Payment.objects.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    extra_context['payment_trends'] = payment_trends or "No payment trends available."

    # Average Payment Amount
    avg_payment = Payment.objects.aggregate(avg=Avg('amount'))['avg'] or 0
    extra_context['avg_payment'] = avg_payment

    # Popular Payment Method
    popular_method = (
        Payment.objects.values('method')
        .annotate(count=Count('method'))
        .order_by('-count')
        .first()
    )
    extra_context['popular_method'] = popular_method['method'] if popular_method else "No data available."

    # Revenue Overview
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    extra_context['total_revenue'] = total_revenue

    return super().changelist_view(request, extra_context=extra_context)


class BillingAudit(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='audit_logs')
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Audit Log for Billing ID {self.billing.id} - {self.field_name}"

    @staticmethod
    def move_to_next_year(accounting_year):
        current_bills = Billing.objects.filter(accounting_year=accounting_year)
        next_year = accounting_year + 1

        for bill in current_bills:
            if bill.closing_balance > 0:
                logger.info(f"Moving balance for {bill.account} to {next_year}.")
                next_year_bill, created = Billing.objects.get_or_create(
                    account=bill.account,
                    accounting_year=next_year,
                    defaults={
                        'brought_forward': bill.closing_balance,
                        'name_mmda': bill.name_mmda,
                        'ghana_card': bill.ghana_card,
                        'recipient_name': bill.recipient_name,
                        'address': bill.address,
                        'contact_number': bill.contact_number,
                        'gps_address': bill.gps_address,
                        'rooms': bill.rooms,
                    }
                )
                if not created:
                    next_year_bill.brought_forward += bill.closing_balance
                    next_year_bill.save(update_fields=['brought_forward'])



def bill_list(request):
    bills = Billing.objects.all()
    logger.info(f"Number of bills: {bills.count()}")  # Log the number of bills
    return render(request, 'billing/bill_list.html', {'bills': bills})



# models.py

class CustomerStatement(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('bill', 'Bill'),
        ('payment', 'Payment'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    payment_id = models.CharField(max_length=50, blank=True, null=True)  # For payments
    customer_name = models.CharField(max_length=255)
    dr_account = models.ForeignKey(DataCapture, on_delete=models.CASCADE, related_name='debits')
    cr_account = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name='credits')
    cr_account_name = models.CharField(max_length=255)
    year_bill = models.PositiveIntegerField()
    date_generated = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)  # Payment method for payments, auto for bills

    def __str__(self):
        return f"{self.transaction_type} - {self.customer_name} - {self.amount}"

    class Meta:
        verbose_name = "Customer Statement"
        verbose_name_plural = "Customer Statements"
        ordering = ['-date_generated']