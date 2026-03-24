import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User, SessionUtilisateur
from users.serializers import UserProfilSerializer

logger = logging.getLogger('kotizo')


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mon_profil(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserProfilSerializer(user)
        return Response({'success': True, 'user': serializer.data})

    serializer = UserProfilSerializer(user, data=request.data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    logger.info({'action': 'profil_modifie', 'user_id': str(user.id)})
    return Response({'success': True, 'user': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_sessions(request):
    sessions = SessionUtilisateur.objects.filter(
        user=request.user, est_active=True
    ).order_by('-date_derniere_activite')
    data = [{
        'id': s.id,
        'device_info': s.device_info,
        'ip': s.ip,
        'date_creation': s.date_creation,
        'date_derniere_activite': s.date_derniere_activite,
    } for s in sessions]
    return Response({'success': True, 'sessions': data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoquer_session(request, session_id):
    try:
        session = SessionUtilisateur.objects.get(id=session_id, user=request.user)
        session.est_active = False
        session.save(update_fields=['est_active'])
        return Response({'success': True, 'message': "Session révoquée."})
    except SessionUtilisateur.DoesNotExist:
        return Response({'success': False, 'erreur': "Session introuvable."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_stats(request):
    from cotisations.models import Cotisation, Participation
    from quickpay.models import QuickPay
    user = request.user
    return Response({
        'success': True,
        'stats': {
            'cotisations_creees': Cotisation.objects.filter(createur=user, supprime=False).count(),
            'cotisations_completes': Cotisation.objects.filter(createur=user, statut='complete').count(),
            'participations': Participation.objects.filter(participant=user, statut='paye').count(),
            'quickpays_crees': QuickPay.objects.filter(createur=user).count(),
            'parrainages': user.nb_parrainages_actifs,
            'niveau': user.niveau,
        }
    })