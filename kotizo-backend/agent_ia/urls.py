from django.urls import path
from .views import historique_messages, envoyer_message

urlpatterns = [
    path('historique/', historique_messages),
    path('message/', envoyer_message),
]