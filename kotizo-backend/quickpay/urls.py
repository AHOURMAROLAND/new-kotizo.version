from django.urls import path
from .views import (
    quickpay_list_create, quickpay_detail,
    quickpay_par_code, payer_quickpay,
    quickpays_recus, stats_quickpay,
)

urlpatterns = [
    path('', quickpay_list_create),
    path('recus/', quickpays_recus),
    path('stats/', stats_quickpay),
    path('code/<str:code>/', quickpay_par_code),
    path('payer/<str:code>/', payer_quickpay),
    path('<uuid:quickpay_id>/', quickpay_detail),
]