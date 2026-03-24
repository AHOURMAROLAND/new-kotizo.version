import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('kotizo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expirer-quickpay': {
        'task': 'quickpay.tasks.expirer_quickpay_expires',
        'schedule': 300,
    },
    'ping-whatsapp': {
        'task': 'agent_ia.tasks.ping_bot_whatsapp',
        'schedule': 300,
    },
    'detection-fraude': {
        'task': 'admin_panel.tasks.detection_fraude_automatique',
        'schedule': 1800,
    },
    'expirer-cotisations': {
        'task': 'cotisations.tasks.expirer_cotisations',
        'schedule': 3600,
    },
    'maj-fenetre-glissante': {
        'task': 'cotisations.tasks.maj_fenetre_glissante',
        'schedule': 3600,
    },
    'supprimer-comptes-non-verifies': {
        'task': 'users.tasks.supprimer_comptes_non_verifies',
        'schedule': 3600,
    },
    'rappels-expiration': {
        'task': 'cotisations.tasks.envoyer_rappels_expiration',
        'schedule': 21600,
    },
    'rapport-journalier': {
        'task': 'admin_panel.tasks.rapport_journalier',
        'schedule': crontab(hour=20, minute=0),
    },
    'reset-compteurs-email': {
        'task': 'notifications.tasks.reset_compteurs_email',
        'schedule': crontab(hour=0, minute=0),
    },
    'reset-compteurs-ia': {
        'task': 'agent_ia.tasks.reset_compteurs_ia',
        'schedule': crontab(hour=0, minute=0),
    },
}