import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger('kotizo')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user, supprime=False
    ).order_by('-date_creation')[:100]
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'success': True, 'notifications': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nb_non_lues(request):
    nb = Notification.objects.filter(
        user=request.user, lue=False, supprime=False
    ).count()
    return Response({'success': True, 'nb_non_lues': nb})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tout_lire(request):
    Notification.objects.filter(
        user=request.user, lue=False, supprime=False
    ).update(lue=True)
    return Response({'success': True, 'message': "Toutes les notifications marquées comme lues."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_lue(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user, supprime=False)
        notif.lue = True
        notif.save(update_fields=['lue'])
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'success': False, 'erreur': "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_notification(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user, supprime=False)
        notif.supprime = True
        notif.date_suppression = timezone.now()
        notif.save(update_fields=['supprime', 'date_suppression'])
        return Response({'success': True, 'message': "Notification supprimée."})
    except Notification.DoesNotExist:
        return Response({'success': False, 'erreur': "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_notification_globale(request):
    if not request.user.is_staff:
        return Response({'success': False, 'erreur': "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

    titre = request.data.get('titre', '').strip()
    message = request.data.get('message', '').strip()
    canal = request.data.get('canal', 'inapp')
    cible = request.data.get('cible', 'tous')

    if not titre or not message:
        return Response({'success': False, 'erreur': "Titre et message requis."}, status=status.HTTP_400_BAD_REQUEST)

    from users.models import User
    users = User.objects.filter(is_active=True)
    if cible != 'tous':
        users = users.filter(niveau=cible)

    nb = 0
    for user in users:
        Notification.objects.create(
            user=user,
            type_notification='systeme',
            titre=titre,
            message=message,
        )
        nb += 1

    logger.info({'action': 'notification_globale_envoyee', 'nb': nb, 'admin': request.user.pseudo})
    return Response({'success': True, 'message': f"Notification envoyée à {nb} utilisateurs."})
