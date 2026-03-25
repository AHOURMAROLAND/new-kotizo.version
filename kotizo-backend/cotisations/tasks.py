from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('kotizo')


@shared_task(queue='high')
def expirer_cotisations():
    from cotisations.models import Cotisation
    expires = Cotisation.objects.filter(
        statut='active',
        date_expiration__lt=timezone.now(),
        supprime=False,
    )
    nb = expires.update(statut='expiree')
    logger.info({'action': 'cotisations_expirees', 'nb': nb})
    return f"{nb} cotisations expirées"


@shared_task(queue='high')
def maj_fenetre_glissante():
    from users.models import User
    from cotisations.models import Cotisation
    il_y_a_7j = timezone.now() - timedelta(days=7)
    users = User.objects.filter(is_active=True)
    for user in users:
        nb = Cotisation.objects.filter(
            createur=user,
            date_creation__gte=il_y_a_7j,
            supprime=False,
        ).count()
        User.objects.filter(id=user.id).update(cotisations_creees_fenetre=nb)
    logger.info({'action': 'fenetre_glissante_mise_a_jour'})
    return "Fenêtre glissante mise à jour"


@shared_task(queue='default')
def envoyer_rappels_expiration():
    from cotisations.models import Cotisation
    dans_12h = timezone.now() + timedelta(hours=12)
    maintenant = timezone.now()
    cotisations = Cotisation.objects.filter(
        statut='active',
        date_expiration__lte=dans_12h,
        date_expiration__gt=maintenant,
        supprime=False,
    ).select_related('createur')

    for cotisation in cotisations:
        if cotisation.participants_payes < cotisation.nombre_participants:
            logger.info({
                'action': 'rappel_expiration_envoye',
                'slug': cotisation.slug,
                'createur': cotisation.createur.pseudo,
            })
    return f"{cotisations.count()} rappels envoyés"


@shared_task(queue='default')
def envoyer_rappel_manuel(cotisation_id):
    from cotisations.models import Cotisation, Participation
    try:
        cotisation = Cotisation.objects.get(id=cotisation_id)
        participants = Participation.objects.filter(
            cotisation=cotisation,
            statut='en_attente',
        ).select_related('participant')
        nb = participants.count()
        logger.info({
            'action': 'rappel_manuel_envoye',
            'slug': cotisation.slug,
            'nb_participants': nb,
        })
        return f"{nb} rappels envoyés"
    except Cotisation.DoesNotExist:
        return "Cotisation introuvable"


@shared_task(queue='high')
def finaliser_cotisation(cotisation_id):
    from cotisations.models import Cotisation
    from core.utils import calculer_frais_kotizo
    try:
        cotisation = Cotisation.objects.get(id=cotisation_id)
        if cotisation.participants_payes >= cotisation.nombre_participants:
            montant_net = float(cotisation.montant_collecte) - float(
                calculer_frais_kotizo(cotisation.montant_collecte)
            )
            cotisation.statut = 'complete'
            cotisation.save(update_fields=['statut'])
            logger.info({
                'action': 'cotisation_finalisee',
                'slug': cotisation.slug,
                'montant_net': montant_net,
            })
        return "Cotisation finalisée"
    except Cotisation.DoesNotExist:
        return "Cotisation introuvable"
