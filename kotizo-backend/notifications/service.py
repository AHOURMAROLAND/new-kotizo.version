import logging
from django.core.cache import cache
from .models import Notification

logger = logging.getLogger('kotizo')

FOURNISSEURS = [
    ('gmail', 500),
    ('brevo', 300),
    ('mailjet', 200),
    ('resend', 100),
]


def creer_notification(user, type_notification, titre, message, data=None):
    notif = Notification.objects.create(
        user=user,
        type_notification=type_notification,
        titre=titre,
        message=message,
        data=data or {},
    )
    envoyer_push_fcm.delay(str(user.id), titre, message)
    return notif


def get_fournisseur_email():
    for nom, limite in FOURNISSEURS:
        key = f'email_count_{nom}'
        count = cache.get(key, 0)
        if count < limite:
            cache.incr(key) if count > 0 else cache.set(key, 1, timeout=86400)
            return nom
    return None


def envoyer_email(destinataire, sujet, corps_html, corps_texte=''):
    fournisseur = get_fournisseur_email()
    if not fournisseur:
        logger.warning({'action': 'email_tous_fournisseurs_satures'})
        return False
    try:
        from django.conf import settings
        import requests
        if fournisseur == 'gmail':
            from django.core.mail import send_mail
            send_mail(sujet, corps_texte, settings.DEFAULT_FROM_EMAIL, [destinataire])
        elif fournisseur == 'brevo':
            requests.post(
                'https://api.brevo.com/v3/smtp/email',
                headers={'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'},
                json={
                    'sender': {'name': 'Kotizo', 'email': 'noreply@kotizo.app'},
                    'to': [{'email': destinataire}],
                    'subject': sujet,
                    'htmlContent': corps_html,
                },
                timeout=10,
            )
        logger.info({'action': 'email_envoye', 'fournisseur': fournisseur, 'destinataire': destinataire})
        return True
    except Exception as e:
        logger.error({'action': 'email_echec', 'fournisseur': fournisseur, 'error': str(e)})
        return False


from celery import shared_task

@shared_task(queue='default')
def envoyer_push_fcm(user_id, titre, message):
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        if not user.fcm_token:
            return
        import requests
        from django.conf import settings
        requests.post(
            'https://fcm.googleapis.com/fcm/send',
            headers={
                'Authorization': f'key={settings.FCM_SERVER_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'to': user.fcm_token,
                'notification': {'title': titre, 'body': message},
            },
            timeout=10,
        )
        logger.info({'action': 'push_envoye', 'user_id': user_id})
    except Exception as e:
        logger.error({'action': 'push_echec', 'error': str(e)})
