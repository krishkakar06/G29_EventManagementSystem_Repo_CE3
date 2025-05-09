import json
import requests
from django.core.management.base import BaseCommand
from Eventmanage1.models import Event
from django.conf import settings
from decimal import Decimal
import datetime

class Command(BaseCommand):
    help = 'Migrate existing events from Django DB to Flask backend API'

    def handle(self, *args, **options):
        events = Event.objects.all()
        url = f"{settings.FLASK_API_URL}/events"
        headers = {'Authorization': f'Bearer {settings.FLASK_API_TOKEN}', 'Content-Type': 'application/json'}

        for event in events:
            data = {
                'title': event.title,
                'description': event.description,
                'type': event.type,
                'price': float(event.price) if isinstance(event.price, Decimal) else event.price,
                'date': event.date if isinstance(event.date, str) else event.date.isoformat() if isinstance(event.date, datetime.date) else str(event.date),
                'location': event.location,
                'image': event.image,
                'organizer_id': event.organizer.flask_user_id if event.organizer and hasattr(event.organizer, 'flask_user_id') else None
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 201:
                    flask_event = response.json()
                    event.flask_id = flask_event.get('id')
                    event.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully migrated event '{event.title}' with Flask ID {event.flask_id}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to migrate event '{event.title}': {response.text}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error migrating event '{event.title}': {str(e)}"))
