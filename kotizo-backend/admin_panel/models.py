from django.db import models
from django.utils import timezone
from users.models import User


class AlerteFraude(models.Model):

    TYPE_CHOICES = [
        ('creation_rapide', 'Création rapide'),
        ('multi_comptes', 'Multi comptes'),
        ('signalements_multiples', 'Signalements multiples'),
        ('numero_suspect', 'Numéro suspect'),
        ('fraude_paydunya', 'Fraude PayDunya'),
        ('injection_ia', 'Injection IA'),
    ]

    STATUT_CHOICES = [
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('faux_positif', 'Faux positif'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertes_fraude')
    type_alerte = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouvelle')
    data = models.JSONField(null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    traite_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='alertes_traitees'
    )

    class Meta:
        db_table = 'alertes_fraude'
        indexes = [
            models.Index(fields=['statut', 'date_creation']),
            models.Index(fields=['user', 'type_alerte']),
        ]

    def __str__(self):
        return f"{self.type_alerte} — @{self.user.pseudo}"


class Sanction(models.Model):

    NIVEAU_CHOICES = [
        (0, 'Avertissement'),
        (1, 'Restriction légère 3j'),
        (2, 'Restriction moyenne 7j'),
        (3, 'Dégradation niveau 30j'),
        (4, 'Fermeture temporaire'),
        (5, 'Bannissement permanent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sanctions')
    niveau = models.IntegerField(choices=NIVEAU_CHOICES)
    raison = models.TextField()
    appliquee_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sanctions_appliquees'
    )
    date_creation = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'sanctions'
        indexes = [
            models.Index(fields=['user', 'active']),
        ]

    def __str__(self):
        return f"Sanction niveau {self.niveau} — @{self.user.pseudo}"


class TicketSupport(models.Model):

    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]

    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('ferme', 'Fermé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    sujet = models.CharField(max_length=200)
    description = models.TextField()
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ouvert')
    cree_par_ia = models.BooleanField(default=False)
    note_resolution = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets_traites'
    )

    class Meta:
        db_table = 'tickets_support'
        indexes = [
            models.Index(fields=['statut', 'priorite']),
            models.Index(fields=['user', 'statut']),
        ]

    def __str__(self):
        return f"Ticket @{self.user.pseudo} — {self.sujet[:50]}"


class PromoVerification(models.Model):
    prix = models.IntegerField(default=500)
    active = models.BooleanField(default=False)
    duree_jours = models.IntegerField(default=7)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    lancee_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='promos_lancees'
    )

    class Meta:
        db_table = 'promos_verification'

    def __str__(self):
        return f"Promo {self.prix} FCFA — {'active' if self.active else 'inactive'}"
