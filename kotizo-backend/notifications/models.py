from django.db import models
from django.utils import timezone
from users.models import User


class Notification(models.Model):

    TYPE_CHOICES = [
        ('paiement_recu', 'Paiement reçu'),
        ('cotisation_complete', 'Cotisation complète'),
        ('cotisation_expiree', 'Cotisation expirée'),
        ('quickpay_expire', 'Quick Pay expiré'),
        ('quickpay_paye', 'Quick Pay payé'),
        ('verification_approuvee', 'Vérification approuvée'),
        ('verification_rejetee', 'Vérification rejetée'),
        ('nouvelle_connexion', 'Nouvelle connexion'),
        ('sanction', 'Sanction'),
        ('remboursement', 'Remboursement'),
        ('ambassadeur', 'Ambassadeur'),
        ('promo_verification', 'Promo vérification'),
        ('rappel_cotisation', 'Rappel cotisation'),
        ('whatsapp_panne', 'WhatsApp en panne'),
        ('systeme', 'Système'),
        ('reponse_commentaire', 'Réponse commentaire'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'lue']),
            models.Index(fields=['user', 'date_creation']),
            models.Index(fields=['supprime']),
        ]
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.type_notification} → @{self.user.pseudo}"
