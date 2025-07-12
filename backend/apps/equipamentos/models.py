# ================================================================
# SUBSTITUIR backend/apps/equipamentos/models.py
# ================================================================

from django.db import models
from datetime import date

class CategoriaEquipamento(models.Model):
    """Categorias de equipamentos para organização"""
    
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    prefixo_codigo = models.CharField(max_length=5, verbose_name="Prefixo do Código")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        ordering = ['codigo']
        verbose_name = 'Categoria de Equipamento'
        verbose_name_plural = 'Categorias de Equipamentos'
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Equipamento(models.Model):
    """Modelo básico para equipamentos"""
    
    FREQUENCIA_CHOICES = [
        ('DIARIO', 'Diário'),
        ('SEMANAL', 'Semanal'),
        ('QUINZENAL', 'Quinzenal'),
        ('MENSAL', 'Mensal'),
    ]
    
    # Campos básicos
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    
    # ✅ MUDANÇA: categoria ao invés de tipo livre
    categoria = models.ForeignKey(
        CategoriaEquipamento,
        on_delete=models.PROTECT,
        related_name='equipamentos',
        verbose_name="Categoria"
    )
    
    # Especificações
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    n_serie = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Número de Série")
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Horímetro")
    
    # Relacionamentos
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, verbose_name="Cliente")
    empreendimento = models.ForeignKey('empreendimentos.Empreendimento', on_delete=models.CASCADE, verbose_name="Empreendimento")
    
    # NR12
    ativo_nr12 = models.BooleanField(default=True, verbose_name="Ativo para NR12")
    frequencia_checklist = models.CharField(max_length=10, choices=FREQUENCIA_CHOICES, default='DIARIO', verbose_name="Frequência do Checklist")
    tipo_nr12 = models.ForeignKey('nr12_checklist.TipoEquipamentoNR12', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo NR12")
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
    
    def __str__(self):
        return f"{self.nome} ({self.categoria.codigo})"
    
    # ✅ ADICIONAR: Propriedade para compatibilidade
    @property
    def tipo(self):
        """Retorna o nome da categoria para compatibilidade"""
        return self.categoria.nome if self.categoria else ''


# Função para criar categorias
def criar_categorias_mandacaru():
    """Cria categorias padrão da Mandacaru"""
    categorias = [
        {'codigo': 'ESC', 'nome': 'Escavadeiras', 'prefixo': 'ESC'},
        {'codigo': 'RET', 'nome': 'Retroescavadeiras', 'prefixo': 'RET'},
        {'codigo': 'CAR', 'nome': 'Carregadeiras', 'prefixo': 'CAR'},
        {'codigo': 'MOT', 'nome': 'Motoniveladoras', 'prefixo': 'MOT'},
        {'codigo': 'ROL', 'nome': 'Rolos Compactadores', 'prefixo': 'ROL'},
        {'codigo': 'TRA', 'nome': 'Tratores', 'prefixo': 'TRA'},
        {'codigo': 'CAM', 'nome': 'Caminhões', 'prefixo': 'CAM'},
        {'codigo': 'GER', 'nome': 'Geradores', 'prefixo': 'GER'},
        {'codigo': 'OUT', 'nome': 'Outros', 'prefixo': 'OUT'},
    ]
    
    for cat_data in categorias:
        CategoriaEquipamento.objects.get_or_create(
            codigo=cat_data['codigo'],
            defaults={
                'nome': cat_data['nome'],
                'prefixo_codigo': cat_data['prefixo'],
                'descricao': f"Categoria para {cat_data['nome'].lower()}"
            }
        )
    
    print("✅ Categorias criadas/atualizadas com sucesso!")