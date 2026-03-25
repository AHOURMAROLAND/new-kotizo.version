from django.urls import path
from .views import (
    cotisations_list_create, cotisation_detail_public,
    rejoindre_cotisation, stopper_cotisation,
    supprimer_cotisation, modifier_cotisation,
    mes_participations, envoyer_commentaire, envoyer_rappel,
)

urlpatterns = [
    path('', cotisations_list_create),
    path('mes-participations/', mes_participations),
    path('<str:slug>/', cotisation_detail_public),
    path('<str:slug>/rejoindre/', rejoindre_cotisation),
    path('<str:slug>/stopper/', stopper_cotisation),
    path('<str:slug>/modifier/', modifier_cotisation),
    path('<str:slug>/supprimer/', supprimer_cotisation),
    path('<str:slug>/commentaire/', envoyer_commentaire),
    path('<str:slug>/rappel/', envoyer_rappel),
]