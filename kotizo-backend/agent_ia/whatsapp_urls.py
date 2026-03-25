from django.urls import path
from agent_ia.whatsapp_views import webhook_whatsapp

urlpatterns = [
    path('webhook/', webhook_whatsapp),
]