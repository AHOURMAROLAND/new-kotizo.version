from celery import shared_task
import logging

logger = logging.getLogger('kotizo')

@shared_task(queue='high')
def traiter_remboursement(remboursement_id):
    from paiements.models import DemandeRemboursement
    from paiements.paydunya import effectuer_payout
    from core.utils import detecter_operateur
    from django.utils import timezone
    try:
        demande = DemandeRemboursement.objects.select_related('user').get(id=remboursement_id)
        operateur = detecter_operateur(demande.user.telephone) or 'MOOV_TOGO'
        result = effectuer_payout(
            montant=float(demande.montant),
            numero=demande.user.telephone,
            operateur=operateur,
            description=f"Remboursement Kotizo — {demande.raison}",
        )
        if result['success']:
            demande.statut = 'approuvee'
            demande.date_traitement = timezone.now()
            demande.save(update_fields=['statut', 'date_traitement'])
            logger.info({'action': 'remboursement_effectue', 'id': remboursement_id})
        else:
            logger.error({'action': 'remboursement_echoue', 'erreur': result['erreur']})
    except DemandeRemboursement.DoesNotExist:
        logger.error({'action': 'remboursement_introuvable', 'id': remboursement_id})
