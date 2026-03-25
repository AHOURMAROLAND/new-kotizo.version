from django.urls import path
from .views import (
    liste_notifications, nb_non_lues, tout_lire,
    marquer_lue, supprimer_notification,
    envoyer_notification_globale,
)

urlpatterns = [
    path('', liste_notifications),
    path('non-lues/', nb_non_lues),
    path('tout-lire/', tout_lire),
    path('admin/envoyer/', envoyer_notification_globale),
    path('<int:notif_id>/lire/', marquer_lue),
    path('<int:notif_id>/', supprimer_notification),
]