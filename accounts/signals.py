# accounts/signals.py or logs/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from accounts.models import Account  # adjust model as needed
from logs.models import AuditLog

@receiver(post_delete, sender=Account)
def log_account_deletion(sender, instance, **kwargs):
    AuditLog.objects.create(
        model_name='Account',
        object_id=str(instance.pk),
        action='DELETE',
        user=None,  # You can improve this by using thread-local storage to access the request.user
        changes=f"Deleted Account: {instance.first_name} {instance.surname}"
    )



