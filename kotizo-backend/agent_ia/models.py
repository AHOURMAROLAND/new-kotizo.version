from django.db import models
from django.utils import timezone
from users.models import User


class MessageIA(models.Model):

    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('assistant', 'Assistant'),
    ]

    SOURCE_CHOICES = [
        ('app', 'Application'),
        ('whatsapp', 'WhatsApp'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_ia')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenu = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='app')
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'messages_ia'
        indexes = [
            models.Index(fields=['user', 'date_creation']),
            models.Index(fields=['source']),
        ]
        ordering = ['date_creation']

    def __str__(self):
        return f"{self.role} @{self.user.pseudo} — {self.contenu[:50]}"
