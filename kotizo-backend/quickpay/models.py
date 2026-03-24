import uuid
from django.db import models
from django.utils import timezone
from users.models import User


class QuickPay(models.Model):

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('paye', 'Payé'),
        ('expire', 'Expiré'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quickpays_crees')
    code = models.CharField(max_length=11, unique=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_avec_frais = models.DecimalField(max_digits=10, decimal_places=2)
    frais_kotizo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_receveur = models.CharField(max_length=20)
    numero_payeur = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    paydunya_token = models.CharField(max_length=200, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_expiration = models.DateTimeField()
    date_paiement = models.DateTimeField(null=True, blank=True)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quickpays'
        indexes = [
            models.Index(fields=['createur', 'statut']),
            models.Index(fields=['code']),
            models.Index(fields=['statut', 'date_expiration']),
        ]

    def __str__(self):
        return f"{self.code} — {self.montant} FCFA — {self.statut}"

    @property
    def est_expire(self):
        return timezone.now() > self.date_expiration
