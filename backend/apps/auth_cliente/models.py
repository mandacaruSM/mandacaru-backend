# 1. ATUALIZAR backend/apps/auth_cliente/models.py
# ================================================================

from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioCliente(AbstractUser):
    """Usuário customizado que pode ser cliente ou admin da Mandacaru"""
    cliente = models.OneToOneField(
        'clientes.Cliente', 
        on_delete=models.CASCADE, 
        related_name='usuario',
        null=True, blank=True,
        verbose_name="Cliente"
    )
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram Chat ID")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Usuário Cliente"
        verbose_name_plural = "Usuários Clientes"

    def __str__(self):
        if self.cliente:
            return f"{self.username} - {self.cliente.razao_social}"
        return f"{self.username} - Admin Mandacaru"

    @property
    def is_cliente(self):
        """Verifica se é um usuário cliente"""
        return self.cliente is not None

    @property
    def is_admin_mandacaru(self):
        """Verifica se é admin da Mandacaru"""
        return self.cliente is None and (self.is_staff or self.is_superuser)
