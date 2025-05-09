from django import forms
from .models import CabBooking
from django.core.exceptions import ValidationError
from django.utils import timezone

class CabBookingForm(forms.ModelForm):
    class Meta:
        model = CabBooking
        fields = ['pickup_location', 'drop_location', 'pickup_time', 'passengers']
        widgets = {
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup address'
            }),
            'drop_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination'
            }),
            'pickup_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'passengers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
        }

    def clean_pickup_time(self):
        pickup_time = self.cleaned_data.get('pickup_time')
        if pickup_time and pickup_time < timezone.now():
            raise ValidationError("Pickup time cannot be in the past.")
        return pickup_time

    def clean_passengers(self):
        passengers = self.cleaned_data.get('passengers')
        if passengers and (passengers < 1 or passengers > 10):
            raise ValidationError("Number of passengers must be between 1 and 10.")
        return passengers