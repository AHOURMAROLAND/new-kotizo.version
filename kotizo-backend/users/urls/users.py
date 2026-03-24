from django.urls import path
from users.views.user_views import (
    mon_profil, mes_sessions,
    revoquer_session, mes_stats,
)

urlpatterns = [
    path('moi/', mon_profil),
    path('moi/stats/', mes_stats),
    path('sessions/', mes_sessions),
    path('sessions/<int:session_id>/', revoquer_session),
]