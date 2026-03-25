import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction, DemandeRemboursement
from .serializers import TransactionSerializer, DemandeRemboursementSerializer
from .paydunya import creer_invoice
from core.utils import calculer_frais_kotizo, detecter_operateur

logger = logging.getLogger('kotizo')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_transactions(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date_creation')[:100]
    serializer = TransactionSerializer(transactions, many=True)
    return Response({'success': True, 'transactions': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payer_cotisation(request, participation_id):
    from cotisations.models import Participation
    try:
        participation = Participation.objects.select_related(
            'cotisation', 'participant'
        ).get(id=participation_id, participant=request.user)
    except Participation.DoesNotExist:
        return Response({'success': False, 'erreur': "Participation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if participation.statut == 'paye':
        return Response({'success': False, 'erreur': "Déjà payé."}, status=status.HTTP_400_BAD_REQUEST)

    montant = float(participation.montant_avec_frais)
    operateur = detecter_operateur(request.user.telephone)

    result = creer_invoice(
        montant=montant,
        description=f"Kotizo — {participation.cotisation.nom}",
        callback_url=f"https://api.kotizo.app/api/webhooks/paydunya/cotisation/",
        cancel_url=f"https://kotizo.app/c/{participation.cotisation.slug}",
        reference=str(participation.id),
    )

    if not result['success']:
        return Response({'success': False, 'erreur': result['erreur']}, status=status.HTTP_502_BAD_GATEWAY)

    participation.paydunya_token = result['token']
    participation.save(update_fields=['paydunya_token'])

    Transaction.objects.create(
        user=request.user,
        type_transaction='payin',
        montant=participation.montant,
        frais_kotizo=calculer_frais_kotizo(participation.montant),
        frais_paydunya=float(participation.montant) * 0.02,
        canal=operateur or '',
        paydunya_token=result['token'],
        cotisation_id=participation.cotisation.id,
        statut='en_attente',
    )

    logger.info({'action': 'paiement_cotisation_initie', 'participation_id': str(participation_id)})
    return Response({
        'success': True,
        'invoice_url': result['invoice_url'],
        'token': result['token'],
        'montant': montant,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statut_paiement(request, participation_id):
    from cotisations.models import Participation
    try:
        participation = Participation.objects.get(
            id=participation_id, participant=request.user
        )
    except Participation.DoesNotExist:
        return Response({'success': False, 'erreur': "Participation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'statut': participation.statut,
        'participation_id': str(participation.id),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demander_remboursement(request):
    serializer = DemandeRemboursementSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    serializer.save(user=request.user)
    return Response({'success': True, 'message': "Demande de remboursement envoyée."}, status=status.HTTP_201_CREATED)
