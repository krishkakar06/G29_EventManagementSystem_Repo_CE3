from django.db import models
from django.contrib.auth.models import User
from Eventmanage1.models import Event  # Adjust app name accordingly

class CabBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=255, blank=True, null=True)  # Add this field
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField()
    passengers = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.event:
            return f"{self.user.username} - {self.pickup_location} to {self.drop_location} (for {self.event.title})"
        elif self.event_name:
            return f"{self.user.username} - {self.pickup_location} to {self.drop_location} (for {self.event_name})"
        return f"{self.user.username} - {self.pickup_location} to {self.drop_location}"