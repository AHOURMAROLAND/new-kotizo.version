from django.urls import path
from .views import historique_transactions, payer_cotisation, statut_paiement, demander_remboursement

app_name = 'paiements'

urlpatterns = [
    path('historique/', historique_transactions),
    path('payer/<uuid:participation_id>/', payer_cotisation),
    path('statut/<uuid:participation_id>/', statut_paiement),
    path('remboursement/', demander_remboursement),
]
