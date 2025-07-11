# 5. ATUALIZAR backend/apps/auth_cliente/admin.py
# ================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCliente

@admin.register(UsuarioCliente)
class UsuarioClienteAdmin(UserAdmin):
    """Admin para usuários clientes"""
    fieldsets = UserAdmin.fieldsets + (
        ('Dados do Cliente', {
            'fields': ('cliente', 'telefone', 'cargo', 'telegram_chat_id', 
                      'whatsapp_number', 'ativo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados do Cliente', {
            'fields': ('cliente', 'telefone', 'cargo', 'ativo')
        }),
    )
    
    list_display = ('username', 'email', 'cliente', 'cargo', 'ativo', 'is_active', 'last_login')
    list_filter = ('ativo', 'is_active', 'cliente', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'cliente__razao_social', 'first_name', 'last_name')
    ordering = ('username',)