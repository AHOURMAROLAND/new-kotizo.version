from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('kotizo')

@shared_task(queue='low')
def supprimer_comptes_non_verifies():
    from users.models import User
    limite = timezone.now() - timedelta(hours=48)
    non_verifies = User.objects.filter(
        email_verifie=False,
        whatsapp_verifie=False,
        date_inscription__lt=limite,
        is_staff=False,
    )
    nb = non_verifies.count()
    non_verifies.delete()
    logger.info({'action': 'comptes_non_verifies_supprimes', 'nb': nb})
    return f"{nb} comptes supprimés"
