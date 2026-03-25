import re
from rest_framework import serializers
from django.conf import settings
from .models import QuickPay
from core.utils import calculer_total_participant, generer_code


class QuickPayCreerSerializer(serializers.Serializer):
    montant = serializers.DecimalField(max_digits=10, decimal_places=2)
    numero_payeur = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_montant(self, value):
        if value < settings.MONTANT_MIN_FCFA:
            raise serializers.ValidationError(f"Montant minimum : {settings.MONTANT_MIN_FCFA} FCFA")
        if value > settings.MONTANT_MAX_FCFA:
            raise serializers.ValidationError(f"Montant maximum : {settings.MONTANT_MAX_FCFA} FCFA")
        return value

    def validate_numero_payeur(self, value):
        if not re.match(r'^\+228[0-9]{8}$', value):
            raise serializers.ValidationError("Format invalide. Exemple : +22890123456")
        return value

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        user = self.context['request'].user
        montant = float(validated_data['montant'])
        montant_avec_frais = calculer_total_participant(montant)
        frais_kotizo = round(montant * settings.KOTIZO_FRAIS_PERCENT, 0)

        code = f"QP-{generer_code(longueur=8)}"
        while QuickPay.objects.filter(code=code).exists():
            code = f"QP-{generer_code(longueur=8)}"

        qp = QuickPay.objects.create(
            createur=user,
            code=code,
            montant=montant,
            montant_avec_frais=montant_avec_frais,
            frais_kotizo=frais_kotizo,
            numero_receveur=user.numero_mobile_money or user.telephone,
            numero_payeur=validated_data['numero_payeur'],
            description=validated_data.get('description', ''),
            date_expiration=timezone.now() + timedelta(hours=settings.LIMITE_QP_HEURES),
        )
        return qp


class QuickPayDetailSerializer(serializers.ModelSerializer):
    createur_pseudo = serializers.CharField(source='createur.pseudo', read_only=True)
    est_expire = serializers.BooleanField(read_only=True)
    deep_link = serializers.SerializerMethodField()
    montant_total_payeur = serializers.DecimalField(
        source='montant_avec_frais', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = QuickPay
        fields = [
            'id', 'code', 'deep_link', 'montant',
            'montant_total_payeur', 'frais_kotizo',
            'numero_receveur', 'numero_payeur',
            'description', 'statut', 'est_expire',
            'date_creation', 'date_expiration', 'date_paiement',
            'createur_pseudo',
        ]

    def get_deep_link(self, obj):
        return f"kotizo.app/qp/{obj.code}"


class QuickPayListSerializer(serializers.ModelSerializer):
    est_expire = serializers.BooleanField(read_only=True)

    class Meta:
        model = QuickPay
        fields = [
            'id', 'code', 'montant', 'montant_avec_frais',
            'statut', 'est_expire', 'date_creation', 'date_expiration',
        ]
