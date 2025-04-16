# calculator/models.py
from django.db import models

class Trip(models.Model):
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    distance = models.FloatField()
    route_url = models.URLField()
    travel_time = models.FloatField()
    mode = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip from {self.start_address} to {self.end_address}"

