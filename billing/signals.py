from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Billing, BillingAudit
import logging


logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Billing)
def log_billing_changes(sender, instance, **kwargs):
    logger.info(f"Signal triggered for Billing ID: {instance.pk}")



@receiver(pre_save, sender=Billing)
def create_audit_log(sender, instance, **kwargs):
    if instance.pk:  # If the object already exists (it's being updated)
        old_instance = Billing.objects.get(pk=instance.pk)
        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(instance, field_name, None)
            if old_value != new_value:  # Only log if the field value changes
                BillingAudit.objects.create(
                    billing=instance,
                    field_name=field_name,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    changed_by=instance.updated_by if hasattr(instance, 'updated_by') else None
                )
