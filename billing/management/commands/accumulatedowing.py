from django.core.management.base import BaseCommand
from billing.models import Billing, AccumulatedOwing
from datetime import datetime

class Command(BaseCommand):
    help = "Process unpaid bills and move amounts to accumulated owing at year-end"

    def handle(self, *args, **kwargs):
        # Get the current accounting year
        current_year = datetime.now().year

        # Filter for unpaid or partially paid bills from the current year
        unpaid_bills = Billing.objects.filter(
            accounting_year=current_year, payment_status='unpaid'
        )

        # Loop through each unpaid bill and move the owed amount to AccumulatedOwing
        for bill in unpaid_bills:
            # Calculate the amount owed
            amount_owing = bill.amount - (bill.amount_due or 0)

            # Create an AccumulatedOwing record
            AccumulatedOwing.objects.create(
                account=bill.account,
                year=current_year,
                amount=amount_owing,
            )

            # Update the bill's status to mark it as archived
            bill.payment_status = 'archived'
            bill.save()

        # Print a success message after processing all bills
        self.stdout.write(self.style.SUCCESS("End-of-year processing completed successfully."))
