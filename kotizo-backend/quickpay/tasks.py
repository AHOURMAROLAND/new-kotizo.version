from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger('kotizo')


@shared_task(queue='high')
def expirer_quickpay_expires():
    from quickpay.models import QuickPay
    expires = QuickPay.objects.filter(
        statut='actif',
        date_expiration__lt=timezone.now(),
        supprime=False,
    )
    nb = expires.update(statut='expire')
    logger.info({'action': 'quickpays_expires', 'nb': nb})
    return f"{nb} Quick Pay expirés"
