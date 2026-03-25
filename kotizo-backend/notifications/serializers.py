from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'type_notification', 'titre',
            'message', 'lue', 'data', 'date_creation',
        ]
