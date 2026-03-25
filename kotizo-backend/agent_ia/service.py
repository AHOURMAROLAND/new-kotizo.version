import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger('kotizo')

MOTS_INTERDITS = [
    'ignore previous', 'ignore les instructions', 'system prompt',
    'tu es maintenant', 'oublie tout', 'jailbreak', 'dan mode',
    'act as', 'pretend you', 'forget your instructions',
    'nouvelle instruction', 'ignorer les règles',
]

PATTERNS_SUSPECTS = [
    '<script', '<?php', 'SELECT *', 'DROP TABLE',
    'javascript:', 'eval(', 'exec(',
]

SYSTEM_PROMPT = """Tu es Koti, l'assistant intelligent de Kotizo — l'application de cotisation collective et de transfert d'argent au Togo et en Afrique francophone.

Ton rôle :
- Aider les utilisateurs à comprendre et utiliser Kotizo
- Répondre aux questions sur les cotisations, Quick Pay, vérification d'identité, parrainages
- Expliquer les frais (0.5% Kotizo + 2% pay-in + 2.5% pay-out = 5% total)
- Guider sur les opérateurs Mobile Money (Moov Money, Mixx by Yas, T-Money)
- Aider à résoudre les problèmes courants

Règles absolues :
- Tu réponds UNIQUEMENT en français
- Tu ne donnes JAMAIS d'informations personnelles sur d'autres utilisateurs
- Tu ne traites JAMAIS de sujets hors de Kotizo et de la finance mobile en Afrique
- Tu es bienveillant, concis et professionnel
- Si tu ne sais pas, tu dis honnêtement que tu ne sais pas

Informations clés Kotizo :
- Montant minimum : 200 FCFA, maximum : 250 000 FCFA
- Durées cotisation : 3, 7, 14, 21 ou 30 jours
- Quick Pay expire en 1 heure
- Niveaux : Basique (gratuit), Vérifié (1000 FCFA), Business (5000 FCFA/an)
- Vérification identité : CNI, CIE, CNE ou carte étudiant"""


def verifier_injection(message):
    msg_lower = message.lower()
    score = 0

    if len(message) > 2000:
        score += 3

    for mot in MOTS_INTERDITS:
        if mot.lower() in msg_lower:
            score += 4

    for pattern in PATTERNS_SUSPECTS:
        if pattern.lower() in msg_lower:
            score += 3

    caracteres_speciaux = sum(1 for c in message if c in '<>{}[]|\\`~')
    if caracteres_speciaux > 10:
        score += 2

    mots = message.split()
    if mots and len(mots) > 3:
        repetitions = max(mots.count(m) for m in set(mots))
        if repetitions > 5:
            score += 2

    return score >= 4, score


def get_compteur_ia(user_id):
    date_today = timezone.now().date().strftime('%Y-%m-%d')
    key = f'ia_msgs_{user_id}_{date_today}'
    return cache.get(key, 0)


def incrementer_compteur_ia(user_id):
    date_today = timezone.now().date().strftime('%Y-%m-%d')
    key = f'ia_msgs_{user_id}_{date_today}'
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=86400)
    return count


def get_limite_ia(user):
    if user.niveau == 'business':
        return settings.IA_MESSAGES_BUSINESS
    elif user.niveau == 'verifie':
        return settings.IA_MESSAGES_VERIFIE
    return settings.IA_MESSAGES_BASIQUE


def envoyer_message_gemini(user, message, historique):
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        messages_gemini = [{'role': 'user', 'parts': [SYSTEM_PROMPT]}]
        messages_gemini.append({'role': 'model', 'parts': ["Compris. Je suis Koti, l'assistant Kotizo. Comment puis-je vous aider ?"]})

        for msg in historique[-20:]:
            role = 'user' if msg.role == 'user' else 'model'
            messages_gemini.append({'role': role, 'parts': [msg.contenu]})

        messages_gemini.append({'role': 'user', 'parts': [message]})

        chat = model.start_chat(history=messages_gemini[:-1])
        response = chat.send_message(message)
        return {'success': True, 'reponse': response.text}

    except Exception as e:
        logger.error({'action': 'gemini_erreur', 'error': str(e)})
        return {
            'success': False,
            'reponse': "Désolé, je rencontre une difficulté technique. Réessayez dans quelques instants ou contactez le support.",
        }
