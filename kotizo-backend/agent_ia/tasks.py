from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger('kotizo')


@shared_task(queue='low')
def reset_compteurs_ia():
    from django.utils import timezone
    from users.models import User
    yesterday = (timezone.now().date() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d')
    users = User.objects.filter(is_active=True).values_list('id', flat=True)
    for uid in users:
        cache.delete(f'ia_msgs_{uid}_{yesterday}')
    logger.info({'action': 'compteurs_ia_reset'})
    return "Compteurs IA réinitialisés"


@shared_task(queue='default')
def ping_bot_whatsapp():
    import requests
    from django.conf import settings
    from admin_panel.models import AlerteFraude
    from users.models import User

    ping_key = 'whatsapp_ping_echecs'
    echecs = cache.get(ping_key, 0)

    try:
        r = requests.get(
            f"{settings.EVOLUTION_API_URL}/instance/fetchInstances",
            headers={'apikey': settings.EVOLUTION_API_KEY},
            timeout=5,
        )
        if r.status_code == 200:
            cache.set(ping_key, 0, timeout=3600)
            cache.set('whatsapp_statut', 'actif', timeout=600)
            logger.info({'action': 'whatsapp_ping_ok'})
        else:
            raise Exception(f"Status {r.status_code}")
    except Exception as e:
        echecs += 1
        cache.set(ping_key, echecs, timeout=3600)
        cache.set('whatsapp_statut', 'hors_service', timeout=600)
        logger.warning({'action': 'whatsapp_ping_echec', 'echecs': echecs})

        if echecs >= 3:
            try:
                admin = User.objects.filter(is_staff=True).first()
                if admin:
                    AlerteFraude.objects.get_or_create(
                        type_alerte='injection_ia',
                        statut='nouvelle',
                        defaults={
                            'user': admin,
                            'description': f"Bot WhatsApp en panne. {echecs} pings échoués. Erreur: {str(e)}",
                        }
                    )
            except Exception:
                pass

    return f"Ping WhatsApp — échecs: {echecs}"
