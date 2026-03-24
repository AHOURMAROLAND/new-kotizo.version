import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, pseudo, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        if not pseudo:
            raise ValueError('Pseudo obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, pseudo=pseudo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pseudo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verifie', True)
        return self.create_user(email, pseudo, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    NIVEAU_CHOICES = [
        ('basique', 'Basique'),
        ('verifie', 'Vérifié'),
        ('business', 'Business'),
    ]

    ADMIN_ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('moderateur', 'Modérateur'),
        ('support', 'Support'),
        ('finance', 'Finance'),
        ('verification', 'Vérification'),
        ('lecteur', 'Lecteur'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    pseudo = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    whatsapp_numero = models.CharField(max_length=20, blank=True)
    whatsapp_verifie = models.BooleanField(default=False)
    email_verifie = models.BooleanField(default=False)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='basique')
    identite_verifiee = models.BooleanField(default=False)
    nom_verrouille = models.BooleanField(default=False)
    numero_cni_hash = models.CharField(max_length=64, blank=True)
    numero_mobile_money = models.CharField(max_length=20, blank=True)
    code_parrainage = models.CharField(max_length=8, unique=True, blank=True)
    parraine_par = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='filleuls'
    )
    nb_parrainages_actifs = models.IntegerField(default=0)
    cotisations_creees_fenetre = models.IntegerField(default=0)
    admin_role = models.CharField(
        max_length=20, choices=ADMIN_ROLE_CHOICES,
        null=True, blank=True
    )
    fcm_token = models.TextField(blank=True)
    ville_approx = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=2, blank=True, default='TG')
    date_inscription = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pseudo', 'nom', 'prenom']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['pseudo']),
            models.Index(fields=['telephone']),
            models.Index(fields=['niveau']),
            models.Index(fields=['pays']),
            models.Index(fields=['date_inscription']),
        ]

    def __str__(self):
        return f"@{self.pseudo}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def peut_creer_cotisation(self):
        from django.utils import timezone
        from datetime import timedelta
        from cotisations.models import Cotisation
        aujourd_hui = timezone.now().date()
        il_y_a_7j = timezone.now() - timedelta(days=7)
        if self.niveau == 'business':
            return True, None
        nb_jour = Cotisation.objects.filter(
            createur=self,
            date_creation__date=aujourd_hui,
            supprime=False
        ).count()
        nb_semaine = Cotisation.objects.filter(
            createur=self,
            date_creation__gte=il_y_a_7j,
            supprime=False
        ).count()
        from django.conf import settings
        if self.niveau == 'verifie':
            if nb_jour >= settings.LIMITE_COTISATIONS_VERIFIE_JOUR:
                return False, f"Limite journalière atteinte ({settings.LIMITE_COTISATIONS_VERIFIE_JOUR}/jour)"
        else:
            if nb_jour >= settings.LIMITE_COTISATIONS_BASIQUE_JOUR:
                return False, f"Limite journalière atteinte ({settings.LIMITE_COTISATIONS_BASIQUE_JOUR}/jour)"
            if nb_semaine >= settings.LIMITE_COTISATIONS_BASIQUE_SEMAINE:
                return False, f"Limite hebdomadaire atteinte ({settings.LIMITE_COTISATIONS_BASIQUE_SEMAINE}/semaine)"
        return True, None


class UserGeoLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='geo_logs')
    ip = models.GenericIPAddressField()
    pays = models.CharField(max_length=100, blank=True)
    pays_code = models.CharField(max_length=2, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timezone_field = models.CharField(max_length=50, blank=True)
    isp = models.CharField(max_length=200, blank=True)
    date_connexion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users_geo_logs'
        indexes = [
            models.Index(fields=['pays_code', 'date_connexion']),
            models.Index(fields=['user', 'date_connexion']),
        ]

    def __str__(self):
        return f"{self.user.pseudo} — {self.ville}, {self.pays_code}"


class VerificationIdentite(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')
    photo_recto_url = models.URLField(blank=True)
    photo_verso_url = models.URLField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    prix_paye = models.IntegerField(null=True, blank=True)
    note_admin = models.TextField(blank=True)
    raison_rejet = models.TextField(blank=True)
    date_soumission = models.DateTimeField(default=timezone.now)
    date_decision = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='verifications_traitees'
    )

    class Meta:
        db_table = 'verifications_identite'

    def __str__(self):
        return f"Vérification @{self.user.pseudo} — {self.statut}"


class SessionUtilisateur(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_info = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    refresh_token_jti = models.CharField(max_length=255, blank=True)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_derniere_activite = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'sessions_utilisateurs'
        indexes = [
            models.Index(fields=['user', 'est_active']),
        ]

    def __str__(self):
        return f"Session @{self.user.pseudo} — {self.device_info}"