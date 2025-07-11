 # 4. ATUALIZAR backend/apps/auth_cliente/urls.py
# ================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioClienteViewSet)

urlpatterns = [
    path('login/', views.login_cliente, name='login_cliente'),
    path('logout/', views.logout_cliente, name='logout_cliente'),
    path('perfil/', views.atualizar_perfil, name='perfil_cliente'),
    path('vincular-telegram/', views.vincular_telegram, name='vincular_telegram'),
    path('', include(router.urls)),
]

