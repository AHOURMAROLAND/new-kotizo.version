import time
import random
import logging
import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger('kotizo')

COMMANDES = {
    'AIDE': "Commandes disponibles :\n- AIDE : ce menu\n- SOLDE : vos transactions\n- COTISER : créer/rejoindre une cotisation\n- PAYER : Quick Pay\n- STAT : vos statistiques\n- SUPPORT : créer un ticket\n- STOP : désactiver les notifications",
    'STOP': "Notifications WhatsApp désactivées. Tapez AIDE pour les réactiver.",
}


def envoyer_message_whatsapp(numero, message):
    time.sleep(random.uniform(3, 6))
    try:
        r = requests.post(
            f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE}",
            headers={
                'apikey': settings.EVOLUTION_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'number': numero,
                'options': {'delay': 1200, 'presence': 'composing'},
                'textMessage': {'text': message},
            },
            timeout=10,
        )
        logger.info({'action': 'whatsapp_envoye', 'numero': numero})
        return r.status_code == 200
    except Exception as e:
        logger.error({'action': 'whatsapp_echec', 'error': str(e)})
        return False


@csrf_exempt
@require_POST
def webhook_whatsapp(request):
    import json
    try:
        data = json.loads(request.body)
        event = data.get('event', '')

        if event != 'messages.upsert':
            return HttpResponse(status=200)

        message_data = data.get('data', {})
        numero = message_data.get('key', {}).get('remoteJid', '').replace('@s.whatsapp.net', '')
        contenu = message_data.get('message', {}).get('conversation', '').strip().upper()

        if not numero or not contenu:
            return HttpResponse(status=200)

        from users.models import User
        try:
            user = User.objects.get(whatsapp_numero__icontains=numero)
        except User.DoesNotExist:
            numero_format = f"+{numero}" if not numero.startswith('+') else numero
            envoyer_message_whatsapp(
                numero_format,
                "Numéro non reconnu. Inscrivez-vous sur l'application Kotizo."
            )
            return HttpResponse(status=200)

        token_key = f'inscription_wa_{user.telephone}'
        token_stocke = None
        from django.core.cache import cache
        token_stocke = cache.get(token_key)

        if token_stocke and contenu == token_stocke:
            user.whatsapp_verifie = True
            user.save(update_fields=['whatsapp_verifie'])
            cache.delete(token_key)
            envoyer_message_whatsapp(
                user.whatsapp_numero,
                "Compte Kotizo verifie avec succes ! Bienvenue sur Kotizo."
            )
            return HttpResponse(status=200)

        if contenu in COMMANDES:
            envoyer_message_whatsapp(user.whatsapp_numero, COMMANDES[contenu])
            return HttpResponse(status=200)

        from agent_ia.models import MessageIA
        from agent_ia.service import (
            verifier_injection, get_compteur_ia,
            incrementer_compteur_ia, envoyer_message_gemini,
        )

        est_injection, _ = verifier_injection(contenu)
        if est_injection:
            envoyer_message_whatsapp(user.whatsapp_numero, "Message non autorisé.")
            return HttpResponse(status=200)

        historique = MessageIA.objects.filter(user=user).order_by('-date_creation')[:20]
        historique = list(reversed(historique))

        MessageIA.objects.create(user=user, role='user', contenu=contenu, source='whatsapp')

        result = envoyer_message_gemini(user, contenu, historique)
        reponse = result['reponse']

        MessageIA.objects.create(user=user, role='assistant', contenu=reponse, source='whatsapp')
        incrementer_compteur_ia(str(user.id))

        envoyer_message_whatsapp(user.whatsapp_numero, reponse)

    except Exception as e:
        logger.error({'action': 'webhook_whatsapp_erreur', 'error': str(e)})

    return HttpResponse(status=200)
