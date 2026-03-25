import logging
from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User, VerificationIdentite
from core.utils import hash_numero_cni

logger = logging.getLogger('kotizo')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def soumettre_verification(request):
    user = request.user

    if user.identite_verifiee:
        return Response({
            'success': False,
            'erreur': "Votre identité est déjà vérifiée.",
        }, status=status.HTTP_400_BAD_REQUEST)

    if VerificationIdentite.objects.filter(user=user, statut='en_attente').exists():
        return Response({
            'success': False,
            'erreur': "Un dossier est déjà en cours de traitement.",
        }, status=status.HTTP_400_BAD_REQUEST)

    photo_recto = request.data.get('photo_recto_url', '').strip()
    photo_verso = request.data.get('photo_verso_url', '').strip()
    numero_cni = request.data.get('numero_cni', '').strip()

    if not photo_recto or not photo_verso:
        return Response({
            'success': False,
            'erreur': "Photos recto et verso obligatoires.",
        }, status=status.HTTP_400_BAD_REQUEST)

    if not numero_cni:
        return Response({
            'success': False,
            'erreur': "Numéro de carte obligatoire.",
        }, status=status.HTTP_400_BAD_REQUEST)

    user.numero_cni_hash = hash_numero_cni(numero_cni)
    user.save(update_fields=['numero_cni_hash'])

    VerificationIdentite.objects.filter(user=user).delete()

    verif = VerificationIdentite.objects.create(
        user=user,
        photo_recto_url=photo_recto,
        photo_verso_url=photo_verso,
        statut='en_attente',
    )

    from notifications.models import Notification
    Notification.objects.create(
        user=user,
        type_notification='systeme',
        titre="Dossier soumis",
        message="Votre dossier de vérification a été soumis. Traitement sous 24-48h.",
    )

    logger.info({'action': 'verification_soumise', 'user': user.pseudo})
    return Response({
        'success': True,
        'message': "Dossier soumis. Vous serez notifié dans 24-48h.",
        'verif_id': verif.id,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statut_verification(request):
    try:
        verif = VerificationIdentite.objects.get(user=request.user)
        return Response({
            'success': True,
            'statut': verif.statut,
            'date_soumission': verif.date_soumission,
            'raison_rejet': verif.raison_rejet if verif.statut == 'rejetee' else None,
        })
    except VerificationIdentite.DoesNotExist:
        return Response({
            'success': True,
            'statut': 'non_soumis',
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demande_business(request):
    user = request.user

    if user.niveau == 'business':
        return Response({'success': False, 'erreur': "Vous êtes déjà Business."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.identite_verifiee:
        return Response({'success': False, 'erreur': "Vérification d'identité requise avant le compte Business."}, status=status.HTTP_400_BAD_REQUEST)

    nom_entreprise = request.data.get('nom_entreprise', '').strip()
    secteur = request.data.get('secteur', '').strip()
    description = request.data.get('description', '').strip()

    if not nom_entreprise or not secteur:
        return Response({'success': False, 'erreur': "Nom entreprise et secteur obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

    from admin_panel.models import TicketSupport
    TicketSupport.objects.create(
        user=user,
        sujet=f"Demande compte Business — {nom_entreprise}",
        description=f"Secteur: {secteur}\nDescription: {description}",
        priorite='haute',
    )

    logger.info({'action': 'demande_business', 'user': user.pseudo})
    return Response({'success': True, 'message': "Demande envoyée. Traitement sous 2-5 jours."})
