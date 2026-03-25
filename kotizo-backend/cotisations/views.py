import logging
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Cotisation, Participation, CommentaireCotisation
from .serializers import (
    CotisationCreerSerializer, CotisationDetailSerializer,
    CotisationListSerializer, RejoindreSerializer, CommentaireSerializer,
)

logger = logging.getLogger('kotizo')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cotisations_list_create(request):
    if request.method == 'GET':
        statut = request.query_params.get('statut')
        qs = Cotisation.objects.filter(supprime=False).select_related('createur')
        if statut:
            qs = qs.filter(statut=statut)
        serializer = CotisationListSerializer(qs[:50], many=True)
        return Response({'success': True, 'cotisations': serializer.data})

    peut, erreur = request.user.peut_creer_cotisation()
    if not peut:
        return Response({'success': False, 'erreur': erreur}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    serializer = CotisationCreerSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    cotisation = serializer.save()
    logger.info({'action': 'cotisation_creee', 'slug': cotisation.slug, 'user': request.user.pseudo})
    return Response({
        'success': True,
        'message': "Cotisation créée.",
        'cotisation': CotisationDetailSerializer(cotisation).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def cotisation_detail_public(request, slug):
    try:
        cotisation = Cotisation.objects.select_related('createur').prefetch_related(
            'participations__participant'
        ).get(slug=slug, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CotisationDetailSerializer(cotisation)
    return Response({'success': True, 'cotisation': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rejoindre_cotisation(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if cotisation.statut != 'active':
        return Response({'success': False, 'erreur': "Cette cotisation n'est plus active."}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now() > cotisation.date_expiration:
        return Response({'success': False, 'erreur': "Cette cotisation a expiré."}, status=status.HTTP_400_BAD_REQUEST)

    if Participation.objects.filter(cotisation=cotisation, participant=request.user, supprime=False).exists():
        return Response({'success': False, 'erreur': "Vous participez déjà à cette cotisation."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RejoindreSerializer(data=request.data, context={'cotisation': cotisation})
    if not serializer.is_valid():
        return Response({'success': False, 'erreur': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    rang = cotisation.participants_payes + 1

    participation = Participation.objects.create(
        cotisation=cotisation,
        participant=request.user,
        montant=data['montant_total'],
        montant_avec_frais=data['montant_avec_frais'],
        nb_unites=data['nb_unites'],
        rang_paiement=rang,
        statut='en_attente',
    )

    logger.info({'action': 'cotisation_rejointe', 'slug': slug, 'user': request.user.pseudo})
    return Response({
        'success': True,
        'message': "Participation enregistrée. Procédez au paiement.",
        'participation_id': str(participation.id),
        'montant_avec_frais': data['montant_avec_frais'],
        'montant': data['montant_total'],
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stopper_cotisation(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, createur=request.user, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if cotisation.statut != 'active':
        return Response({'success': False, 'erreur': "Cotisation déjà arrêtée."}, status=status.HTTP_400_BAD_REQUEST)

    cotisation.statut = 'stoppee'
    cotisation.stoppee_le = timezone.now()
    cotisation.save(update_fields=['statut', 'stoppee_le'])

    logger.info({'action': 'cotisation_stoppee', 'slug': slug})
    return Response({'success': True, 'message': "Collecte arrêtée. Suppression possible dans 48h."})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_cotisation(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, createur=request.user, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if not cotisation.peut_etre_supprimee:
        return Response({
            'success': False,
            'erreur': "Vous devez stopper la cotisation et attendre 48h avant de supprimer."
        }, status=status.HTTP_400_BAD_REQUEST)

    cotisation.supprime = True
    cotisation.date_suppression = timezone.now()
    cotisation.supprime_par = request.user
    cotisation.save(update_fields=['supprime', 'date_suppression', 'supprime_par'])

    logger.info({'action': 'cotisation_supprimee', 'slug': slug})
    return Response({'success': True, 'message': "Cotisation supprimée de votre historique."})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_cotisation(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, createur=request.user, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if cotisation.participants_payes > 0:
        return Response({
            'success': False,
            'erreur': "Modification impossible : des participants ont déjà payé."
        }, status=status.HTTP_400_BAD_REQUEST)

    champs_modifiables = ['nom', 'description', 'montant_unitaire']
    for champ in champs_modifiables:
        if champ in request.data:
            setattr(cotisation, champ, request.data[champ])
    cotisation.save()

    return Response({'success': True, 'cotisation': CotisationDetailSerializer(cotisation).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_participations(request):
    participations = Participation.objects.filter(
        participant=request.user, supprime=False
    ).select_related('cotisation__createur').order_by('-date_participation')

    data = []
    for p in participations:
        data.append({
            'id': str(p.id),
            'cotisation_slug': p.cotisation.slug,
            'cotisation_nom': p.cotisation.nom,
            'createur_pseudo': p.cotisation.createur.pseudo,
            'montant': float(p.montant),
            'montant_avec_frais': float(p.montant_avec_frais),
            'nb_unites': p.nb_unites,
            'statut': p.statut,
            'rang_paiement': p.rang_paiement,
            'date_participation': p.date_participation,
            'date_paiement': p.date_paiement,
        })
    return Response({'success': True, 'participations': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_commentaire(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    from datetime import timedelta
    participation = Participation.objects.filter(
        cotisation=cotisation, participant=request.user
    ).first()

    if not participation:
        return Response({'success': False, 'erreur': "Vous ne participez pas à cette cotisation."}, status=status.HTTP_403_FORBIDDEN)

    limite = participation.date_participation + timedelta(days=60)
    if timezone.now() > limite:
        return Response({'success': False, 'erreur': "Commentaires fermés (plus de 2 mois)."}, status=status.HTTP_400_BAD_REQUEST)

    message = request.data.get('message', '').strip()
    if not message:
        return Response({'success': False, 'erreur': "Message vide."}, status=status.HTTP_400_BAD_REQUEST)

    commentaire = CommentaireCotisation.objects.create(
        cotisation=cotisation,
        auteur=request.user,
        message=message,
    )
    logger.info({'action': 'commentaire_envoye', 'slug': slug, 'user': request.user.pseudo})
    return Response({'success': True, 'message': "Commentaire envoyé."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_rappel(request, slug):
    try:
        cotisation = Cotisation.objects.get(slug=slug, createur=request.user, supprime=False)
    except Cotisation.DoesNotExist:
        return Response({'success': False, 'erreur': "Cotisation introuvable."}, status=status.HTTP_404_NOT_FOUND)

    if cotisation.statut != 'active':
        return Response({'success': False, 'erreur': "Cotisation inactive."}, status=status.HTTP_400_BAD_REQUEST)

    from cotisations.tasks import envoyer_rappel_manuel
    envoyer_rappel_manuel.delay(str(cotisation.id))

    return Response({'success': True, 'message': "Rappels envoyés aux participants."})
