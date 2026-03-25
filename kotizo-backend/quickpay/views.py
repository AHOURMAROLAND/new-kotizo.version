import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import QuickPay
from .serializers import QuickPayCreerSerializer, QuickPayDetailSerializer, QuickPayListSerializer
from paiements.paydunya import creer_invoice
from core.utils import detecter_operateur

logger = logging.getLogger('kotizo')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quickpay_list_create(request):
    if request.method == 'GET':
        qps = QuickPay.objects.filter(
            createur=request.user, supprime=False
        ).order_by('-date_creation')[:50]
        serializer = QuickPayListSerializer(qps, many=True)
        return Response({'success': True, 'quickpays': serializer.data})

    if not request.user.numero_mobile_money and not request.user.telephone:
        return Response({
            'success': False,
            'erreur': "Ajoutez un numéro Mobile Money dans votre profil avant de créer un Quick Pay."
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = QuickPayCreerSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    qp = serializer.save()
    logger.info({'action': 'quickpay_cree', 'code': qp.code, 'user': request.user.pseudo})

    return Response({
        'success': True,
        'message': "Quick Pay créé.",
        'quickpay': QuickPayDetailSerializer(qp).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def quickpay_detail(request, quickpay_id):
    try:
        qp = QuickPay.objects.select_related('createur').get(id=quickpay_id, supprime=False)
    except QuickPay.DoesNotExist:
        return Response({'success': False, 'erreur': "Quick Pay introuvable."}, status=status.HTTP_404_NOT_FOUND)

    return Response({'success': True, 'quickpay': QuickPayDetailSerializer(qp).data})


@api_view(['GET'])
@permission_classes([AllowAny])
def quickpay_par_code(request, code):
    try:
        qp = QuickPay.objects.select_related('createur').get(code=code, supprime=False)
    except QuickPay.DoesNotExist:
        return Response({'success': False, 'erreur': "Quick Pay introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if qp.est_expire and qp.statut == 'actif':
        qp.statut = 'expire'
        qp.save(update_fields=['statut'])

    return Response({'success': True, 'quickpay': QuickPayDetailSerializer(qp).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def payer_quickpay(request, code):
    try:
        qp = QuickPay.objects.get(code=code, supprime=False)
    except QuickPay.DoesNotExist:
        return Response({'success': False, 'erreur': "Quick Pay introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if qp.statut != 'actif':
        return Response({
            'success': False,
            'erreur': f"Ce Quick Pay est {qp.statut}."
        }, status=status.HTTP_400_BAD_REQUEST)

    if qp.est_expire:
        qp.statut = 'expire'
        qp.save(update_fields=['statut'])
        return Response({'success': False, 'erreur': "Ce Quick Pay a expiré."}, status=status.HTTP_400_BAD_REQUEST)

    operateur = detecter_operateur(qp.numero_payeur)

    result = creer_invoice(
        montant=float(qp.montant_avec_frais),
        description=f"Kotizo Quick Pay {qp.code}",
        callback_url="https://api.kotizo.app/api/webhooks/paydunya/quickpay/",
        cancel_url=f"https://kotizo.app/qp/{qp.code}",
        reference=str(qp.id),
    )

    if not result['success']:
        return Response({'success': False, 'erreur': result['erreur']}, status=status.HTTP_502_BAD_GATEWAY)

    qp.paydunya_token = result['token']
    qp.save(update_fields=['paydunya_token'])

    from paiements.models import Transaction
    from core.utils import calculer_frais_kotizo
    Transaction.objects.create(
        user=qp.createur,
        type_transaction='payin',
        montant=qp.montant,
        frais_kotizo=calculer_frais_kotizo(qp.montant),
        frais_paydunya=float(qp.montant) * 0.02,
        canal=operateur or '',
        paydunya_token=result['token'],
        quickpay_id=qp.id,
        statut='en_attente',
    )

    logger.info({'action': 'quickpay_paiement_initie', 'code': qp.code})
    return Response({
        'success': True,
        'invoice_url': result['invoice_url'],
        'token': result['token'],
        'montant': float(qp.montant_avec_frais),
        'montant_net': float(qp.montant),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quickpays_recus(request):
    from paiements.models import Transaction
    tokens_payes = Transaction.objects.filter(
        user=request.user,
        type_transaction='payin',
        statut='complete',
        quickpay_id__isnull=False,
    ).values_list('quickpay_id', flat=True)

    qps = QuickPay.objects.filter(
        id__in=tokens_payes
    ).order_by('-date_paiement')

    serializer = QuickPayDetailSerializer(qps, many=True)
    return Response({'success': True, 'quickpays_recus': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_quickpay(request):
    user = request.user
    qps = QuickPay.objects.filter(createur=user, supprime=False)
    return Response({
        'success': True,
        'stats': {
            'total_crees': qps.count(),
            'total_payes': qps.filter(statut='paye').count(),
            'total_expires': qps.filter(statut='expire').count(),
            'volume_envoye': sum(float(q.montant) for q in qps.filter(statut='paye')),
        }
    })
