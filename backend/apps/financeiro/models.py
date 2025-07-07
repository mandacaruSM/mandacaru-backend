# apps/financeiro/models.py
from django.db import models
from clientes.models import Cliente
from fornecedores.models import Fornecedor

class ContaFinanceira(models.Model):
    TIPO_CHOICES = [
        ("pagar", "Conta a Pagar"),
        ("receber", "Conta a Receber")
    ]
    FORMA_PAGAMENTO = [
        ("Pix", "Pix"),
        ("Boleto", "Boleto"),
        ("Transferência", "Transferência"),
        ("Dinheiro", "Dinheiro"),
        ("Cartão", "Cartão")
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO)
    status = models.CharField(max_length=20, default="pendente")
    comprovante = models.ImageField(upload_to="comprovantes/", null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    fornecedor = models.ForeignKey(Fornecedor, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_despesa = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.descricao} - R$ {self.valor}"

# apps/financeiro/serializers.py
from rest_framework import serializers
from .models import ContaFinanceira

class ContaFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaFinanceira
        fields = '__all__'

# apps/financeiro/views.py
from rest_framework import viewsets
from .models import ContaFinanceira
from .serializers import ContaFinanceiraSerializer

class ContaFinanceiraViewSet(viewsets.ModelViewSet):
    queryset = ContaFinanceira.objects.all()
    serializer_class = ContaFinanceiraSerializer

# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.financeiro.views import ContaFinanceiraViewSet

router = DefaultRouter()
router.register(r'financeiro/contas', ContaFinanceiraViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

# settings.py (trecho importante para arquivos de imagem)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py (completar)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
