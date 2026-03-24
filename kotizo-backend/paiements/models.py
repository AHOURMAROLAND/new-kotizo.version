import uuid
from django.db import models
from django.utils import timezone
from users.models import User


class Transaction(models.Model):

    TYPE_CHOICES = [
        ('payin', 'Pay-in'),
        ('payout', 'Pay-out'),
        ('remboursement', 'Remboursement'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complète'),
        ('echoue', 'Échouée'),
    ]

    CANAL_CHOICES = [
        ('MOOV_TOGO', 'Moov Money'),
        ('MIXX_TOGO', 'Mixx by Yas'),
        ('TMONEY_TOGO', 'T-Money'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    frais_kotizo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_paydunya = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, blank=True)
    paydunya_token = models.CharField(max_length=200, blank=True)
    paydunya_reference = models.CharField(max_length=200, blank=True)
    cotisation_id = models.UUIDField(null=True, blank=True)
    quickpay_id = models.UUIDField(null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['user', 'statut']),
            models.Index(fields=['type_transaction', 'statut']),
            models.Index(fields=['date_creation']),
            models.Index(fields=['paydunya_token']),
        ]

    def __str__(self):
        return f"{self.type_transaction} — {self.montant} FCFA — {self.statut}"


class DemandeRemboursement(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_remboursement')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    raison = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    note_admin = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='remboursements_traites'
    )

    class Meta:
        db_table = 'demandes_remboursements'
        indexes = [
            models.Index(fields=['statut', 'date_creation']),
        ]

    def __str__(self):
        return f"Remboursement @{self.user.pseudo} — {self.montant} FCFA"
