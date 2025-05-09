from django.contrib import admin
from .models import CabBooking

@admin.register(CabBooking)
class CabBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'pickup_location', 'drop_location', 'pickup_time', 'passengers', 'event', 'event_name', 'booked_at')
    search_fields = ('user__username', 'pickup_location', 'drop_location', 'event__title', 'event_name')
    list_filter = ('pickup_time', 'event', 'booked_at')
    raw_id_fields = ('user', 'event')