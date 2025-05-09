import requests
from rest_framework import serializers
from .models import Event
from django.conf import settings

class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='flask_id', read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    type = serializers.CharField(max_length=50)
    price = serializers.FloatField()
    date = serializers.CharField(max_length=50)
    location = serializers.CharField(max_length=200)
    image = serializers.URLField(required=False)
    organizer_id = serializers.IntegerField()

    def create(self, validated_data):
        try:
            response = requests.post(
                f"{settings.FLASK_API_URL}/events",
                json=validated_data,
                headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
            )
            response.raise_for_status()
            return Event.objects.get(flask_id=response.json()['id'])
        except requests.RequestException as e:
            raise serializers.ValidationError(f"Error creating event in Flask API: {e}")

    def update(self, instance, validated_data):
        try:
            response = requests.put(
                f"{settings.FLASK_API_URL}/events/{instance.flask_id}",
                json=validated_data,
                headers={'Authorization': f'Bearer {settings.FLASK_API_TOKEN}'}
            )
            response.raise_for_status()
            return instance
        except requests.RequestException as e:
            raise serializers.ValidationError(f"Error updating event in Flask API: {e}")
