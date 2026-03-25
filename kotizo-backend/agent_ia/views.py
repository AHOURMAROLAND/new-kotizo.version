import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MessageIA
from .service import (
    verifier_injection, get_compteur_ia,
    incrementer_compteur_ia, get_limite_ia,
    envoyer_message_gemini,
)

logger = logging.getLogger('kotizo')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_messages(request):
    messages = MessageIA.objects.filter(
        user=request.user
    ).order_by('-date_creation')[:100]
    messages = list(reversed(messages))
    data = [{
        'id': m.id,
        'role': m.role,
        'contenu': m.contenu,
        'source': m.source,
        'date_creation': m.date_creation,
    } for m in messages]
    return Response({'success': True, 'messages': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_message(request):
    user = request.user
    message = request.data.get('message', '').strip()
    source = request.data.get('source', 'app')

    if not message:
        return Response({'success': False, 'erreur': "Message vide."}, status=status.HTTP_400_BAD_REQUEST)

    if len(message) > 2000:
        return Response({'success': False, 'erreur': "Message trop long (max 2000 caractères)."}, status=status.HTTP_400_BAD_REQUEST)

    est_injection, score = verifier_injection(message)
    if est_injection:
        from admin_panel.models import AlerteFraude
        AlerteFraude.objects.create(
            user=user,
            type_alerte='injection_ia',
            description=f"Tentative injection IA détectée. Score: {score}. Message: {message[:200]}",
            data={'score': score, 'message': message[:500]},
        )
        logger.warning({'action': 'injection_ia_bloquee', 'user': user.pseudo, 'score': score})
        return Response({
            'success': False,
            'erreur': "Message non autorisé.",
        }, status=status.HTTP_400_BAD_REQUEST)

    limite = get_limite_ia(user)
    compteur = get_compteur_ia(str(user.id))

    if compteur >= limite:
        return Response({
            'success': False,
            'erreur': f"Limite journalière atteinte ({limite} messages). Continuez sur WhatsApp.",
            'limite_atteinte': True,
            'whatsapp_link': f"https://wa.me/{'+22800000000'}?text=Bonjour+Koti",
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    historique = MessageIA.objects.filter(user=user).order_by('-date_creation')[:20]
    historique = list(reversed(historique))

    MessageIA.objects.create(user=user, role='user', contenu=message, source=source)

    result = envoyer_message_gemini(user, message, historique)
    reponse = result['reponse']

    MessageIA.objects.create(user=user, role='assistant', contenu=reponse, source=source)

    incrementer_compteur_ia(str(user.id))
    nouveau_compteur = get_compteur_ia(str(user.id))

    logger.info({'action': 'message_ia_envoye', 'user': user.pseudo, 'compteur': nouveau_compteur})

    return Response({
        'success': True,
        'reponse': reponse,
        'compteur': nouveau_compteur,
        'limite': limite,
        'messages_restants': max(0, limite - nouveau_compteur),
    })
