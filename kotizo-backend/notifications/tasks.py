from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger('kotizo')


@shared_task(queue='low')
def reset_compteurs_email():
    fournisseurs = ['gmail', 'brevo', 'mailjet', 'resend']
    for nom in fournisseurs:
        cache.delete(f'email_count_{nom}')
    logger.info({'action': 'compteurs_email_reset'})
    return "Compteurs email réinitialisés"


@shared_task(queue='default')
def envoyer_notification_paiement(user_id, cotisation_nom, montant):
    from users.models import User
    from notifications.service import creer_notification
    try:
        user = User.objects.get(id=user_id)
        creer_notification(
            user=user,
            type_notification='paiement_recu',
            titre="Paiement confirmé",
            message=f"Votre paiement de {montant} FCFA pour '{cotisation_nom}' a été confirmé.",
            data={'montant': montant, 'cotisation': cotisation_nom},
        )
    except User.DoesNotExist:
        pass


@shared_task(queue='default')
def envoyer_notification_cotisation_complete(cotisation_id):
    from cotisations.models import Cotisation, Participation
    from notifications.service import creer_notification
    try:
        cotisation = Cotisation.objects.select_related('createur').get(id=cotisation_id)
        creer_notification(
            user=cotisation.createur,
            type_notification='cotisation_complete',
            titre="Cotisation complète !",
            message=f"Votre cotisation '{cotisation.nom}' est complète. Le reversement est en cours.",
            data={'slug': cotisation.slug},
        )
        participants = Participation.objects.filter(
            cotisation=cotisation, statut='paye'
        ).select_related('participant')
        for p in participants:
            creer_notification(
                user=p.participant,
                type_notification='cotisation_complete',
                titre="Cotisation complète !",
                message=f"La cotisation '{cotisation.nom}' est complète.",
                data={'slug': cotisation.slug},
            )
    except Cotisation.DoesNotExist:
        pass
