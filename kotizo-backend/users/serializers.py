import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.conf import settings
from .models import User, VerificationIdentite, SessionUtilisateur
from core.utils import hash_numero_cni, generer_code


class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'prenom', 'nom', 'pseudo', 'email',
            'telephone', 'whatsapp_numero',
            'password', 'password_confirm'
        ]

    def validate_pseudo(self, value):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', value):
            raise serializers.ValidationError("Pseudo invalide. Lettres, chiffres et _ uniquement (3-20 chars).")
        if User.objects.filter(pseudo__iexact=value).exists():
            raise serializers.ValidationError("Ce pseudo est déjà pris.")
        return value.lower()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value.lower()

    def validate_telephone(self, value):
        if not re.match(r'^\+228[0-9]{8}$', value):
            raise serializers.ValidationError("Format invalide. Exemple : +22890123456")
        return value

    def validate_whatsapp_numero(self, value):
        if not re.match(r'^\+228[0-9]{8}$', value):
            raise serializers.ValidationError("Format invalide. Exemple : +22890123456")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        code = generer_code(longueur=8)
        while User.objects.filter(code_parrainage=code).exists():
            code = generer_code(longueur=8)
        user = User(**validated_data, code_parrainage=code)
        user.set_password(password)
        user.save()
        return user


class ConnexionSerializer(serializers.Serializer):
    identifiant = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifiant = data.get('identifiant', '').strip()
        password = data.get('password', '')
        user = None
        if '@' in identifiant:
            try:
                u = User.objects.get(email__iexact=identifiant)
                user = authenticate(username=u.email, password=password)
            except User.DoesNotExist:
                pass
        else:
            try:
                u = User.objects.get(pseudo__iexact=identifiant)
                user = authenticate(username=u.email, password=password)
            except User.DoesNotExist:
                pass
        if not user:
            raise serializers.ValidationError("Identifiant ou mot de passe incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        if not user.email_verifie and not user.whatsapp_verifie:
            raise serializers.ValidationError("Compte non vérifié. Vérifiez votre email ou WhatsApp.")
        data['user'] = user
        return data


class VerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)


class VerificationWhatsAppSerializer(serializers.Serializer):
    telephone = serializers.CharField()
    token = serializers.CharField()


class MotDePasseOublieSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Aucun compte avec cet email.")
        return value.lower()


class ChangerMotDePasseSerializer(serializers.Serializer):
    ancien_password = serializers.CharField(write_only=True)
    nouveau_password = serializers.CharField(write_only=True, min_length=8)
    nouveau_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['nouveau_password'] != data['nouveau_password_confirm']:
            raise serializers.ValidationError({'nouveau_password_confirm': "Les mots de passe ne correspondent pas."})
        return data


class VerifierCNISerializer(serializers.Serializer):
    numero_cni = serializers.CharField()


class UserProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'pseudo', 'prenom', 'nom', 'email',
            'telephone', 'whatsapp_numero', 'whatsapp_verifie',
            'email_verifie', 'niveau', 'identite_verifiee',
            'numero_mobile_money', 'code_parrainage',
            'nb_parrainages_actifs', 'pays', 'ville_approx',
            'date_inscription', 'fcm_token',
        ]
        read_only_fields = [
            'id', 'email', 'email_verifie', 'whatsapp_verifie',
            'niveau', 'identite_verifiee', 'code_parrainage',
            'nb_parrainages_actifs', 'date_inscription',
        ]

    def validate_pseudo(self, value):
        user = self.context['request'].user
        if User.objects.filter(pseudo__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Ce pseudo est déjà pris.")
        return value.lower()

    def update(self, instance, validated_data):
        if instance.nom_verrouille:
            validated_data.pop('nom', None)
            validated_data.pop('prenom', None)
        return super().update(instance, validated_data)
