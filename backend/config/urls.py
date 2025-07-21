# ================================================================
# URLs PRINCIPAIS PARA BOT
# backend/config/urls.py (adicionar essas linhas)
# ================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs principais
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),
    path('api/operadores/', include('backend.apps.operadores.api_urls')),
    
    # ✅ CRÍTICO: URLs específicas para BOT
    path('bot/', include('backend.apps.nr12_checklist.urls_bot')),
    
    # URLs para QR codes (se existir)
    path('qr/', include('backend.apps.nr12_checklist.urls_qr')),
]

# Servir arquivos de média em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
