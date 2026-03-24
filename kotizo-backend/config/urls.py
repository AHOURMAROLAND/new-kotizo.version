from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('users.urls.auth')),
    path('api/users/', include('users.urls.users')),
    path('api/cotisations/', include('cotisations.urls')),
    path('api/paiements/', include('paiements.urls')),
    path('api/quickpay/', include('quickpay.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/agent-ia/', include('agent_ia.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
    path('api/webhooks/', include('paiements.webhook_urls')),
    path('api/whatsapp/', include('agent_ia.whatsapp_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)