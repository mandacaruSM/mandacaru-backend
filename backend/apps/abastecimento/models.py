# ----------------------------------------------------------------
# 4. ATUALIZAR MODELS PARA CORRIGIR IMPORTS
# backend/apps/abastecimento/models.py - VERSÃO CORRIGIDA
# ----------------------------------------------------------------

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from backend.apps.equipamentos.models import Equipamento

User = get_user_model()

class TipoCombustivel(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    unidade_medida = models.CharField(max_length=10, default='Litros')
    preco_medio = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de Combustível'
        verbose_name_plural = 'Tipos de Combustível'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_estoque_almoxarifado(self):
        """Retorna o estoque do almoxarifado para este combustível"""
        try:
            from backend.apps.almoxarifado.models import EstoqueCombustivel
            return EstoqueCombustivel.objects.get(tipo_combustivel=self)
        except:
            return None

    @property
    def quantidade_disponivel_almoxarifado(self):
        """Quantidade disponível no almoxarifado"""
        estoque = self.get_estoque_almoxarifado()
        return estoque.quantidade_em_estoque if estoque else Decimal('0.000')

    @property
    def estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        estoque = self.get_estoque_almoxarifado()
        return estoque.abaixo_do_minimo if estoque else False


class RegistroAbastecimento(models.Model):
    TIPO_MEDICAO_CHOICES = [
        ('HORIMETRO', 'Horímetro'),
        ('QUILOMETRAGEM', 'Quilometragem'),
    ]
    ORIGEM_COMBUSTIVEL_CHOICES = [
        ('ALMOXARIFADO', 'Almoxarifado'),
        ('POSTO_EXTERNO', 'Posto Externo'),
    ]

    numero = models.CharField(max_length=20, unique=True, editable=False)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='abastecimentos')

    origem_combustivel = models.CharField(
        max_length=20,
        choices=ORIGEM_COMBUSTIVEL_CHOICES,
        default='POSTO_EXTERNO',
        verbose_name="Origem do Combustível",
        help_text="Selecione 'Almoxarifado' para baixa automática no estoque"
    )

    data_abastecimento = models.DateTimeField()
    data_registro = models.DateTimeField(auto_now_add=True)

    tipo_combustivel = models.ForeignKey(TipoCombustivel, on_delete=models.CASCADE)
    quantidade_litros = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        help_text="Quantidade que será descontada do estoque se origem for Almoxarifado"
    )
    preco_litro = models.DecimalField(max_digits=10, decimal_places=3)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    # Campos de validação para almoxarifado
    estoque_antes_abastecimento = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        null=True, 
        blank=True,
        verbose_name="Estoque Antes (Litros)",
        help_text="Estoque registrado antes do abastecimento"
    )
    estoque_depois_abastecimento = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        null=True, 
        blank=True,
        verbose_name="Estoque Depois (Litros)",
        help_text="Estoque após a baixa automática"
    )

    tipo_medicao = models.CharField(max_length=15, choices=TIPO_MEDICAO_CHOICES, default='HORIMETRO')
    medicao_atual = models.DecimalField(max_digits=10, decimal_places=2)
    medicao_anterior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    posto_combustivel = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)

    aprovado = models.BooleanField(default=False)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovou_abastecimentos')
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    foto_painel = models.ImageField(upload_to='abastecimentos/paineis/', blank=True, null=True)
    nota_fiscal = models.FileField(upload_to='abastecimentos/notas/', blank=True, null=True)

    registrado_via_bot = models.BooleanField(default=False)
    chat_id_telegram = models.CharField(max_length=50, blank=True)
    operador_codigo = models.CharField(max_length=20, blank=True)

    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abastecimentos_criados')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro de Abastecimento'
        verbose_name_plural = 'Registros de Abastecimento'
        ordering = ['-data_abastecimento']
        indexes = [
            models.Index(fields=['equipamento', 'data_abastecimento']),
            models.Index(fields=['numero']),
            models.Index(fields=['aprovado']),
            models.Index(fields=['origem_combustivel']),
        ]

    def clean(self):
        super().clean()
        
        # Validação específica para almoxarifado
        if self.origem_combustivel == 'ALMOXARIFADO':
            self._validar_estoque_almoxarifado()

    def _validar_estoque_almoxarifado(self):
        """Valida se há estoque suficiente no almoxarifado"""
        try:
            from backend.apps.almoxarifado.models import EstoqueCombustivel
            
            estoque = EstoqueCombustivel.objects.get(
                tipo_combustivel=self.tipo_combustivel,
                ativo=True
            )
            
            if estoque.quantidade_em_estoque < self.quantidade_litros:
                raise ValidationError({
                    'quantidade_litros': f'Estoque insuficiente no almoxarifado. '
                                       f'Disponível: {estoque.quantidade_em_estoque}L, '
                                       f'Solicitado: {self.quantidade_litros}L'
                })
            
            # Alerta de estoque baixo após o abastecimento
            estoque_pos_abastecimento = estoque.quantidade_em_estoque - self.quantidade_litros
            if estoque_pos_abastecimento <= estoque.estoque_minimo:
                self.observacoes += f"\n⚠️ ALERTA: Estoque ficará baixo após abastecimento ({estoque_pos_abastecimento}L)"
                
        except:
            raise ValidationError({
                'tipo_combustivel': f'Combustível {self.tipo_combustivel.nome} não cadastrado no almoxarifado. '
                                  f'Configure o estoque antes de usar como origem.'
            })

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.gerar_numero()

        self.valor_total = self.quantidade_litros * self.preco_litro

        if not self.medicao_anterior:
            self.medicao_anterior = self._obter_medicao_anterior()

        super().save(*args, **kwargs)

    def gerar_numero(self):
        hoje = date.today()
        prefixo = f"AB{hoje.strftime('%Y%m')}"
        ultimo = RegistroAbastecimento.objects.filter(numero__startswith=prefixo).order_by('numero').last()
        novo_num = 1 if not ultimo else int(ultimo.numero[-4:]) + 1
        return f"{prefixo}{novo_num:04d}"

    def _obter_medicao_anterior(self):
        """Método para obter medição anterior"""
        anterior = RegistroAbastecimento.objects.filter(
            equipamento=self.equipamento,
            data_abastecimento__lt=self.data_abastecimento
        ).exclude(id=self.id).order_by('-data_abastecimento').first()

        if anterior:
            return anterior.medicao_atual

        return Decimal('0.00')

    @property
    def consumo_periodo(self):
        if not self.medicao_anterior or self.medicao_atual <= self.medicao_anterior:
            return None
        return round(self.quantidade_litros / (self.medicao_atual - self.medicao_anterior), 2)

    def __str__(self):
        origem_icon = "🏪" if self.origem_combustivel == "ALMOXARIFADO" else "⛽"
        return f"{origem_icon} {self.numero} - {self.equipamento.nome}"