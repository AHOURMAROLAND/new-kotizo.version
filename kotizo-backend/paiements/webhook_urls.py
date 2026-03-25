from django.urls import path
from paiements.webhooks import webhook_cotisation, webhook_quickpay, webhook_payout

urlpatterns = [
    path('paydunya/cotisation/', webhook_cotisation),
    path('paydunya/quickpay/', webhook_quickpay),
    path('paydunya/payout/', webhook_payout),
]