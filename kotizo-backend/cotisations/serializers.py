from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Cotisation, Participation, CommentaireCotisation
from core.utils import generer_code, calculer_frais_kotizo, calculer_total_participant


class CotisationCreerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotisation
        fields = [
            'nom', 'description', 'montant_unitaire',
            'nombre_participants', 'nb_jours',
            'numero_receveur', 'est_recurrente', 'config_recurrence',
        ]

    def validate_montant_unitaire(self, value):
        if value < settings.MONTANT_MIN_FCFA:
            raise serializers.ValidationError(f"Montant minimum : {settings.MONTANT_MIN_FCFA} FCFA")
        if value > settings.MONTANT_MAX_FCFA:
            raise serializers.ValidationError(f"Montant maximum : {settings.MONTANT_MAX_FCFA} FCFA")
        return value

    def validate_nombre_participants(self, value):
        if value < 2:
            raise serializers.ValidationError("Minimum 2 participants.")
        return value

    def validate_nb_jours(self, value):
        if value not in [3, 7, 14, 21, 30]:
            raise serializers.ValidationError("Durée invalide. Choisir : 3, 7, 14, 21 ou 30 jours.")
        return value

    def validate_numero_receveur(self, value):
        import re
        if not re.match(r'^\+228[0-9]{8}$', value):
            raise serializers.ValidationError("Format invalide. Exemple : +22890123456")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        slug = f"KTZ-{generer_code(longueur=12)}"
        while Cotisation.objects.filter(slug=slug).exists():
            slug = f"KTZ-{generer_code(longueur=12)}"
        date_expiration = timezone.now() + timedelta(days=validated_data['nb_jours'])
        cotisation = Cotisation.objects.create(
            createur=user,
            slug=slug,
            deep_link=f"kotizo.app/c/{slug}",
            date_expiration=date_expiration,
            **validated_data
        )
        return cotisation


class ParticipationSerializer(serializers.ModelSerializer):
    participant_pseudo = serializers.CharField(source='participant.pseudo', read_only=True)
    participant_niveau = serializers.CharField(source='participant.niveau', read_only=True)

    class Meta:
        model = Participation
        fields = [
            'id', 'participant_pseudo', 'participant_niveau',
            'montant', 'montant_avec_frais', 'nb_unites',
            'statut', 'rang_paiement', 'date_participation', 'date_paiement',
        ]


class CotisationDetailSerializer(serializers.ModelSerializer):
    createur_pseudo = serializers.CharField(source='createur.pseudo', read_only=True)
    createur_niveau = serializers.CharField(source='createur.niveau', read_only=True)
    progression = serializers.FloatField(read_only=True)
    participations = ParticipationSerializer(many=True, read_only=True)
    frais_kotizo = serializers.SerializerMethodField()
    montant_total_si_complet = serializers.FloatField(read_only=True)

    class Meta:
        model = Cotisation
        fields = [
            'id', 'slug', 'deep_link', 'nom', 'description',
            'montant_unitaire', 'nombre_participants', 'participants_payes',
            'montant_collecte', 'nb_jours', 'date_creation', 'date_expiration',
            'statut', 'numero_receveur', 'est_recurrente', 'config_recurrence',
            'createur_pseudo', 'createur_niveau',
            'progression', 'participations',
            'frais_kotizo', 'montant_total_si_complet',
        ]

    def get_frais_kotizo(self, obj):
        return calculer_frais_kotizo(obj.montant_unitaire)


class CotisationListSerializer(serializers.ModelSerializer):
    createur_pseudo = serializers.CharField(source='createur.pseudo', read_only=True)
    progression = serializers.FloatField(read_only=True)

    class Meta:
        model = Cotisation
        fields = [
            'id', 'slug', 'deep_link', 'nom', 'montant_unitaire',
            'nombre_participants', 'participants_payes', 'progression',
            'statut', 'date_expiration', 'createur_pseudo',
        ]


class RejoindreSerializer(serializers.Serializer):
    nb_unites = serializers.IntegerField(min_value=1, default=1)
    montant_modifie = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False, allow_null=True
    )

    def validate(self, data):
        cotisation = self.context['cotisation']
        nb_unites = data.get('nb_unites', 1)
        montant_modifie = data.get('montant_modifie')
        montant_base = float(cotisation.montant_unitaire)

        if montant_modifie:
            if float(montant_modifie) < montant_base:
                raise serializers.ValidationError({
                    'montant_modifie': f"Le montant doit être supérieur ou égal à {montant_base} FCFA"
                })
            montant_unitaire = float(montant_modifie)
        else:
            montant_unitaire = montant_base

        total = montant_unitaire * nb_unites
        if total > 25000:
            raise serializers.ValidationError(
                f"Le total ({total} FCFA) dépasse la limite de 25 000 FCFA par participation."
            )

        data['montant_unitaire_final'] = montant_unitaire
        data['montant_total'] = total
        data['montant_avec_frais'] = calculer_total_participant(total)
        return data


class CommentaireSerializer(serializers.ModelSerializer):
    auteur_pseudo = serializers.CharField(source='auteur.pseudo', read_only=True)

    class Meta:
        model = CommentaireCotisation
        fields = ['id', 'auteur_pseudo', 'message', 'reponse_admin', 'date_creation', 'date_reponse']
        read_only_fields = ['reponse_admin', 'date_reponse']
