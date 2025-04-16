from django.db import models


class Billing(models.Model):
    customer = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

class Payment(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=50)  # Ensure this field exists
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure this field exists