from rest_framework import serializers
from .models import Transaction, DemandeRemboursement


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'type_transaction', 'montant',
            'frais_kotizo', 'frais_paydunya',
            'statut', 'canal', 'paydunya_reference',
            'date_creation',
        ]


class DemandeRemboursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeRemboursement
        fields = ['id', 'montant', 'raison', 'description', 'statut', 'date_creation']
        read_only_fields = ['statut']

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Montant invalide.")
        return value
