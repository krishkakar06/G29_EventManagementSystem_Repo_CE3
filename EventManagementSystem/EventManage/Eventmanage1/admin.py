from django.contrib import admin
from .models import Event, Booking, Ticket, Profile, Contact

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'type', 'price', 'location', 'organizer')
    search_fields = ('title', 'type', 'organizer__username', 'location')
    list_filter = ('date', 'type')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'type', 'organizer')
        }),
        ('Event Details', {
            'fields': ('date', 'price', 'location')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event', 'user_name', 'user_email', 'tickets')
    search_fields = ('user_name', 'user_email', 'event__title')
    list_filter = ('event',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'quantity', 'booking_date')
    search_fields = ('user__username', 'event__title')
    list_filter = ('booking_date', 'event')
    raw_id_fields = ('user', 'event')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company_name', 'organization_type', 'country')
    search_fields = ('email', 'company_name', 'first_name', 'last_name')
    list_filter = ('organization_type', 'country')
    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Company Info', {
            'fields': ('company_name', 'organization_type')
        }),
        ('Additional Info', {
            'fields': ('country', 'tickets_planned', 'average_cost', 'reason')
        }),
    )