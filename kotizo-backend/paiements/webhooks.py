import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .paydunya import valider_hash_webhook
from .models import Transaction

logger = logging.getLogger('kotizo')


@csrf_exempt
@require_POST
def webhook_cotisation(request):
    if not valider_hash_webhook(request):
        logger.warning({'action': 'webhook_hash_invalide', 'type': 'cotisation'})
        return HttpResponse(status=400)

    statut = request.POST.get('data[status]', '')
    token = request.POST.get('data[invoice_token]', '')

    if statut != 'completed':
        return HttpResponse(status=200)

    try:
        from cotisations.models import Participation
        participation = Participation.objects.select_related(
            'cotisation', 'participant'
        ).get(paydunya_token=token)

        if participation.statut == 'paye':
            return HttpResponse(status=200)

        participation.statut = 'paye'
        participation.date_paiement = timezone.now()
        participation.save(update_fields=['statut', 'date_paiement'])

        cotisation = participation.cotisation
        cotisation.participants_payes += 1
        cotisation.montant_collecte = float(cotisation.montant_collecte) + float(participation.montant)
        cotisation.save(update_fields=['participants_payes', 'montant_collecte'])

        Transaction.objects.filter(paydunya_token=token).update(statut='complete')

        if cotisation.participants_payes >= cotisation.nombre_participants:
            from cotisations.tasks import finaliser_cotisation
            finaliser_cotisation.delay(str(cotisation.id))

        logger.info({
            'action': 'paiement_cotisation_confirme',
            'slug': cotisation.slug,
            'user': participation.participant.pseudo,
        })

    except Participation.DoesNotExist:
        logger.error({'action': 'webhook_participation_introuvable', 'token': token})

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def webhook_quickpay(request):
    if not valider_hash_webhook(request):
        logger.warning({'action': 'webhook_hash_invalide', 'type': 'quickpay'})
        return HttpResponse(status=400)

    statut = request.POST.get('data[status]', '')
    token = request.POST.get('data[invoice_token]', '')

    if statut != 'completed':
        return HttpResponse(status=200)

    try:
        from quickpay.models import QuickPay
        from .paydunya import effectuer_payout
        from core.utils import detecter_operateur

        qp = QuickPay.objects.get(paydunya_token=token)

        if qp.statut == 'paye':
            return HttpResponse(status=200)

        qp.statut = 'paye'
        qp.date_paiement = timezone.now()
        qp.save(update_fields=['statut', 'date_paiement'])

        Transaction.objects.filter(paydunya_token=token).update(statut='complete')

        operateur = detecter_operateur(qp.numero_receveur) or 'MOOV_TOGO'
        montant_net = float(qp.montant)
        effectuer_payout(
            montant=montant_net,
            numero=qp.numero_receveur,
            operateur=operateur,
            description=f"Kotizo Quick Pay {qp.code}",
        )

        logger.info({'action': 'quickpay_confirme', 'code': qp.code})

    except QuickPay.DoesNotExist:
        logger.error({'action': 'webhook_quickpay_introuvable', 'token': token})

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def webhook_payout(request):
    if not valider_hash_webhook(request):
        return HttpResponse(status=400)

    statut = request.POST.get('data[status]', '')
    reference = request.POST.get('data[transaction_id]', '')

    logger.info({
        'action': 'webhook_payout_recu',
        'statut': statut,
        'reference': reference,
    })

    Transaction.objects.filter(
        paydunya_reference=reference,
        type_transaction='payout',
    ).update(
        statut='complete' if statut == 'completed' else 'echoue'
    )

    return HttpResponse(status=200)
