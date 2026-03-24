from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views.auth_views import (
    inscription, verification_email, connexion,
    mot_de_passe_oublie, changer_mot_de_passe,
    deconnexion, verifier_token,
)

urlpatterns = [
    path('inscription/', inscription),
    path('connexion/', connexion),
    path('deconnexion/', deconnexion),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('verification-email/', verification_email),
    path('mot-de-passe-oublie/', mot_de_passe_oublie),
    path('changer-mot-de-passe/', changer_mot_de_passe),
    path('verifier-token/', verifier_token),
]