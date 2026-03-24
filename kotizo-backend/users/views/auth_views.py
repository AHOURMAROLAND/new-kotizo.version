import random
import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from users.models import User, SessionUtilisateur, UserGeoLog
from users.serializers import (
    InscriptionSerializer, ConnexionSerializer,
    VerificationOTPSerializer, MotDePasseOublieSerializer,
    ChangerMotDePasseSerializer, VerifierCNISerializer,
)
from core.utils import get_client_ip, get_geo_from_ip, hash_numero_cni

logger = logging.getLogger('kotizo')


def generer_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def verifier_blocage_inscription(telephone):
    key = f'inscription_tentatives_{telephone}'
    tentatives = cache.get(key, 0)
    return tentatives >= 3, tentatives


def incrementer_tentatives(telephone):
    key = f'inscription_tentatives_{telephone}'
    tentatives = cache.get(key, 0) + 1
    cache.set(key, tentatives, timeout=86400)
    return tentatives


@api_view(['POST'])
@permission_classes([AllowAny])
def inscription(request):
    bloque, nb = verifier_blocage_inscription(request.data.get('telephone', ''))
    if bloque:
        return Response({
            'success': False,
            'erreur': f"Trop de tentatives. Ce numéro est bloqué pendant 24h.",
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    serializer = InscriptionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    otp = str(random.randint(100000, 999999))
    cache.set(f'inscription_email_{user.email}', otp, timeout=300)
    cache.set(f'inscription_wa_{user.telephone}', otp, timeout=300)

    logger.info({'action': 'inscription', 'user_id': str(user.id), 'pseudo': user.pseudo})

    return Response({
        'success': True,
        'message': "Compte créé. Choisissez votre canal de vérification.",
        'user_id': str(user.id),
        'email': user.email,
        'telephone': user.telephone,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def verification_email(request):
    serializer = VerificationOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()
    otp_saisi = serializer.validated_data['otp']
    otp_stocke = cache.get(f'inscription_email_{email}')

    if not otp_stocke:
        return Response({
            'success': False,
            'erreur': "OTP expiré. Veuillez recommencer l'inscription.",
        }, status=status.HTTP_400_BAD_REQUEST)

    if otp_saisi != otp_stocke:
        incrementer_tentatives(request.data.get('telephone', email))
        return Response({'success': False, 'erreur': "Code incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'success': False, 'erreur': "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

    user.email_verifie = True
    user.save(update_fields=['email_verifie'])
    cache.delete(f'inscription_email_{email}')

    tokens = generer_tokens(user)
    logger.info({'action': 'email_verifie', 'user_id': str(user.id)})

    return Response({'success': True, 'message': "Email vérifié.", 'tokens': tokens})


@api_view(['POST'])
@permission_classes([AllowAny])
def connexion(request):
    serializer = ConnexionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data['user']

    if user.identite_verifiee:
        numero_cni = request.data.get('numero_cni', '')
        if not numero_cni:
            return Response({
                'success': False,
                'erreur': "Saisie du numéro CNI requise.",
                'require_cni': True,
            }, status=status.HTTP_200_OK)
        if hash_numero_cni(numero_cni) != user.numero_cni_hash:
            return Response({'success': False, 'erreur': "Numéro CNI incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    SessionUtilisateur.objects.filter(user=user, est_active=True).update(est_active=False)

    ip = get_client_ip(request)
    device = request.META.get('HTTP_USER_AGENT', '')[:200]

    session = SessionUtilisateur.objects.create(user=user, ip=ip, device_info=device)

    geo = get_geo_from_ip(ip)
    if geo:
        UserGeoLog.objects.create(user=user, ip=ip, **geo)
        if geo.get('pays_code'):
            user.pays = geo['pays_code']
            user.ville_approx = geo.get('ville', '')
            user.save(update_fields=['pays', 'ville_approx'])

    tokens = generer_tokens(user)
    logger.info({'action': 'connexion', 'user_id': str(user.id), 'ip': ip})

    return Response({
        'success': True,
        'tokens': tokens,
        'user': {
            'id': str(user.id),
            'pseudo': user.pseudo,
            'prenom': user.prenom,
            'nom': user.nom,
            'email': user.email,
            'niveau': user.niveau,
            'identite_verifiee': user.identite_verifiee,
            'whatsapp_verifie': user.whatsapp_verifie,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def mot_de_passe_oublie(request):
    serializer = MotDePasseOublieSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    token = str(random.randint(100000, 999999))
    cache.set(f'reset_mdp_{email}', token, timeout=900)

    logger.info({'action': 'reset_mdp_demande', 'email': email})

    return Response({'success': True, 'message': "Instructions envoyées par email."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changer_mot_de_passe(request):
    from users.serializers import ChangerMotDePasseSerializer
    serializer = ChangerMotDePasseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(serializer.validated_data['ancien_password']):
        return Response({'success': False, 'erreur': "Ancien mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['nouveau_password'])
    user.save()
    logger.info({'action': 'mdp_change', 'user_id': str(user.id)})

    return Response({'success': True, 'message': "Mot de passe modifié."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deconnexion(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        SessionUtilisateur.objects.filter(user=request.user, est_active=True).update(est_active=False)
        logger.info({'action': 'deconnexion', 'user_id': str(request.user.id)})
    except Exception:
        pass
    return Response({'success': True, 'message': "Déconnecté."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verifier_token(request):
    return Response({'success': True, 'valid': True})