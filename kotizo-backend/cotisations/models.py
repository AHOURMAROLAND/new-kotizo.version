import uuid
from django.db import models
from django.utils import timezone
from users.models import User


class Cotisation(models.Model):

    STATUT_CHOICES = [
        ('active', 'Active'),
        ('complete', 'Complète'),
        ('expiree', 'Expirée'),
        ('stoppee', 'Stoppée'),
    ]

    DUREE_CHOICES = [3, 7, 14, 21, 30]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotisations_creees')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    montant_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_participants = models.IntegerField()
    participants_payes = models.IntegerField(default=0)
    montant_collecte = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nb_jours = models.IntegerField()
    date_creation = models.DateTimeField(default=timezone.now)
    date_expiration = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    slug = models.CharField(max_length=16, unique=True)
    deep_link = models.CharField(max_length=200, blank=True)
    numero_receveur = models.CharField(max_length=20)
    est_recurrente = models.BooleanField(default=False)
    config_recurrence = models.JSONField(null=True, blank=True)
    paydunya_invoice_url = models.URLField(blank=True)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)
    supprime_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='cotisations_supprimees'
    )
    stoppee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cotisations'
        indexes = [
            models.Index(fields=['createur', 'statut']),
            models.Index(fields=['slug']),
            models.Index(fields=['statut', 'date_expiration']),
            models.Index(fields=['supprime']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        return f"{self.nom} — {self.slug}"

    @property
    def progression(self):
        if self.nombre_participants == 0:
            return 0
        return round((self.participants_payes / self.nombre_participants) * 100, 1)

    @property
    def montant_total_si_complet(self):
        return float(self.montant_unitaire) * self.nombre_participants

    @property
    def peut_etre_supprimee(self):
        if not self.stoppee_le:
            return False
        delai = timezone.now() - self.stoppee_le
        return delai.total_seconds() >= 48 * 3600


class Participation(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('rembourse', 'Remboursé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='participations')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_avec_frais = models.DecimalField(max_digits=10, decimal_places=2)
    nb_unites = models.IntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    rang_paiement = models.IntegerField(null=True, blank=True)
    paydunya_token = models.CharField(max_length=200, blank=True)
    date_participation = models.DateTimeField(default=timezone.now)
    date_paiement = models.DateTimeField(null=True, blank=True)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'participations'
        unique_together = ('cotisation', 'participant')
        indexes = [
            models.Index(fields=['cotisation', 'statut']),
            models.Index(fields=['participant', 'statut']),
            models.Index(fields=['supprime']),
        ]

    def __str__(self):
        return f"@{self.participant.pseudo} → {self.cotisation.nom}"


class CommentaireCotisation(models.Model):
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    message = models.TextField()
    reponse_admin = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_reponse = models.DateTimeField(null=True, blank=True)
    supprime = models.BooleanField(default=False)

    class Meta:
        db_table = 'commentaires_cotisations'
        indexes = [
            models.Index(fields=['cotisation', 'date_creation']),
        ]

    def __str__(self):
        return f"Commentaire @{self.auteur.pseudo} sur {self.cotisation.nom}"
