# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import SignalMessage, PoliceStation, DeliveryReport

@receiver(post_save, sender=SignalMessage)
def handle_signal_delivery(sender, instance, created, **kwargs):
    if created and instance.status == 'SENT':
        # Determine recipient stations based on hierarchy
        stations = PoliceStation.objects.none()
        
        # Check hierarchy from most specific to most general
        if instance.station:
            stations = PoliceStation.objects.filter(id=instance.station.id)
        elif instance.district:
            stations = PoliceStation.objects.filter(district=instance.district)
        elif instance.division:
            stations = PoliceStation.objects.filter(district__division=instance.division)
        elif instance.police_region:
            stations = PoliceStation.objects.filter(
                district__division__police_region=instance.police_region
            )
        
        # Create delivery reports for each station
        for station in stations.distinct():
            DeliveryReport.objects.create(
                message=instance,
                recipient_unit=station  # Changed from police_region to station
            )
        
        # Update cache
        cache.set(f'signal_update_{instance.id}', True, timeout=300)