# municipal_data/models.py
from django.db import models

# models.py

class UserAssignment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="assignment")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        assigned = f"Region: {self.region.name}" if self.region else "Unassigned"
        if self.mmda:
            assigned += f", MMDA: {self.mmda.name}"
        return f"{self.user.username} - {assigned}"
