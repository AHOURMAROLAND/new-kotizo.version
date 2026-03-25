import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User

logger = logging.getLogger('kotizo')

SEUILS = {
    'ambassadeur_verifie': {'parrainages': 50, 'filleuls_actifs': 25},
    'ambassadeur_business': {'parrainages': 100, 'filleuls_actifs': 50},
}


def get_filleuls_actifs_verifie(user):
    return user.filleuls.filter(
        cotisations_creees__supprime=False
    ).annotate(
        nb_cot=__import__('django.db.models', fromlist=['Count']).Count('cotisations_creees')
    ).filter(nb_cot__gte=3).distinct().count()


def get_filleuls_actifs_business(user):
    from django.db.models import Count, Q
    from cotisations.models import Participation
    filleuls = user.filleuls.all()
    actifs = 0
    for f in filleuls:
        nb_cot = f.cotisations_creees.filter(supprime=False).count()
        nb_qp = f.quickpays_crees.filter(supprime=False).count()
        if (nb_cot + nb_qp) >= 3:
            actifs += 1
    return actifs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_parrainage(request):
    user = request.user
    total_filleuls = user.filleuls.count()
    filleuls_actifs_verifie = get_filleuls_actifs_verifie(user)
    filleuls_actifs_business = get_filleuls_actifs_business(user)
    nb_parrainages = user.nb_parrainages_actifs

    progression_verifie = min(100, max(
        (nb_parrainages / SEUILS['ambassadeur_verifie']['parrainages']) * 100,
        (filleuls_actifs_verifie / SEUILS['ambassadeur_verifie']['filleuls_actifs']) * 100,
    ))

    progression_business = min(100, max(
        (nb_parrainages / SEUILS['ambassadeur_business']['parrainages']) * 100,
        (filleuls_actifs_business / SEUILS['ambassadeur_business']['filleuls_actifs']) * 100,
    ))

    eligible_verifie = (
        nb_parrainages >= SEUILS['ambassadeur_verifie']['parrainages'] or
        filleuls_actifs_verifie >= SEUILS['ambassadeur_verifie']['filleuls_actifs']
    )

    eligible_business = (
        nb_parrainages >= SEUILS['ambassadeur_business']['parrainages'] or
        filleuls_actifs_business >= SEUILS['ambassadeur_business']['filleuls_actifs']
    )

    return Response({
        'success': True,
        'code_parrainage': user.code_parrainage,
        'lien_parrainage': f"kotizo.app/ref/{user.code_parrainage}",
        'stats': {
            'total_filleuls': total_filleuls,
            'nb_parrainages_actifs': nb_parrainages,
            'filleuls_actifs_verifie': filleuls_actifs_verifie,
            'filleuls_actifs_business': filleuls_actifs_business,
        },
        'progression': {
            'vers_ambassadeur_verifie': round(progression_verifie, 1),
            'vers_ambassadeur_business': round(progression_business, 1),
        },
        'eligible_ambassadeur_verifie': eligible_verifie,
        'eligible_ambassadeur_business': eligible_business,
        'seuils': SEUILS,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def appliquer_code_parrainage(request):
    code = request.data.get('code', '').strip().upper()
    user = request.user

    if user.parraine_par:
        return Response({'success': False, 'erreur': "Vous avez déjà un parrain."}, status=400)

    try:
        parrain = User.objects.get(code_parrainage=code)
    except User.DoesNotExist:
        return Response({'success': False, 'erreur': "Code de parrainage invalide."}, status=400)

    if parrain.id == user.id:
        return Response({'success': False, 'erreur': "Vous ne pouvez pas vous parrainer vous-même."}, status=400)

    user.parraine_par = parrain
    user.save(update_fields=['parraine_par'])

    parrain.nb_parrainages_actifs += 1
    parrain.save(update_fields=['nb_parrainages_actifs'])

    logger.info({'action': 'parrainage_applique', 'filleul': user.pseudo, 'parrain': parrain.pseudo})
    return Response({'success': True, 'message': f"Parrain @{parrain.pseudo} enregistré."})
