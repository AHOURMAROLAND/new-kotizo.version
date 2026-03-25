from django.urls import path
from users.views.user_views import mon_profil, mes_sessions, revoquer_session, mes_stats
from users.views.verification_views import soumettre_verification, statut_verification, demande_business
from users.views.parrainage_views import stats_parrainage, appliquer_code_parrainage

urlpatterns = [
    path('moi/', mon_profil),
    path('moi/stats/', mes_stats),
    path('sessions/', mes_sessions),
    path('sessions/<int:session_id>/', revoquer_session),
    path('verification/soumettre/', soumettre_verification),
    path('verification/statut/', statut_verification),
    path('demande-business/', demande_business),
    path('parrainage/stats/', stats_parrainage),
    path('parrainage/appliquer/', appliquer_code_parrainage),
]