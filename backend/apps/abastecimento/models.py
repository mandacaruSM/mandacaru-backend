# backend/apps/abastecimento/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from backend.apps.equipamentos.models import Equipamento
from backend.apps.manutencao.models import HistoricoManutencao

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
        verbose_name="Origem do Combustível"
    )

    data_abastecimento = models.DateTimeField()
    data_registro = models.DateTimeField(auto_now_add=True)

    tipo_combustivel = models.ForeignKey(TipoCombustivel, on_delete=models.CASCADE)
    quantidade_litros = models.DecimalField(max_digits=10, decimal_places=3)
    preco_litro = models.DecimalField(max_digits=10, decimal_places=3)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

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
        ]

    def clean(self):
        super().clean()

        if self.tipo_medicao == 'HORIMETRO':
            self._validar_horimetro_com_manutencao()

        self._validar_sequencia_abastecimentos()

        if not self.medicao_anterior:
            self.medicao_anterior = self._obter_medicao_anterior()

    def _validar_horimetro_com_manutencao(self):
        ultima = HistoricoManutencao.objects.filter(
            equipamento=self.equipamento,
            data__lte=self.data_abastecimento.date()
        ).order_by('-data', '-horimetro').first()

        if ultima and self.medicao_atual < ultima.horimetro:
            raise ValidationError({
                'medicao_atual': f'Horímetro ({self.medicao_atual}) menor que última manutenção ({ultima.horimetro})'
            })

        proxima = HistoricoManutencao.objects.filter(
            equipamento=self.equipamento,
            data__gt=self.data_abastecimento.date()
        ).order_by('data', 'horimetro').first()

        if proxima and self.medicao_atual > proxima.horimetro:
            raise ValidationError({
                'medicao_atual': f'Horímetro ({self.medicao_atual}) maior que próxima manutenção ({proxima.horimetro})'
            })

    def _validar_sequencia_abastecimentos(self):
        anterior = RegistroAbastecimento.objects.filter(
            equipamento=self.equipamento,
            data_abastecimento__lt=self.data_abastecimento
        ).exclude(id=self.id).order_by('-data_abastecimento').first()

        if anterior and self.medicao_atual <= anterior.medicao_atual:
            raise ValidationError({
                'medicao_atual': f'Medidor deve ser maior que abastecimento anterior ({anterior.medicao_atual})'
            })

        posterior = RegistroAbastecimento.objects.filter(
            equipamento=self.equipamento,
            data_abastecimento__gt=self.data_abastecimento
        ).exclude(id=self.id).order_by('data_abastecimento').first()

        if posterior and self.medicao_atual >= posterior.medicao_atual:
            raise ValidationError({
                'medicao_atual': f'Medidor deve ser menor que próximo abastecimento ({posterior.medicao_atual})'
            })

    def _obter_medicao_anterior(self):
        anterior = RegistroAbastecimento.objects.filter(
            equipamento=self.equipamento,
            data_abastecimento__lt=self.data_abastecimento
        ).exclude(id=self.id).order_by('-data_abastecimento').first()

        if anterior:
            return anterior.medicao_atual

        manutencao = HistoricoManutencao.objects.filter(
            equipamento=self.equipamento,
            data__lt=self.data_abastecimento.date()
        ).order_by('-data', '-horimetro').first()

        if manutencao:
            return manutencao.horimetro

        return Decimal('0.00')

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

    @property
    def consumo_periodo(self):
        if not self.medicao_anterior or self.medicao_atual <= self.medicao_anterior:
            return None
        return round(self.quantidade_litros / (self.medicao_atual - self.medicao_anterior), 2)

    @property
    def rendimento(self):
        if not self.medicao_anterior or self.medicao_atual <= self.medicao_anterior:
            return None
        return round((self.medicao_atual - self.medicao_anterior) / self.quantidade_litros, 2)

    def __str__(self):
        return f"{self.numero} - {self.equipamento.nome} - {self.data_abastecimento.strftime('%d/%m/%Y')}"


class RelatorioConsumo(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    total_litros = models.DecimalField(max_digits=10, decimal_places=3)
    total_valor = models.DecimalField(max_digits=10, decimal_places=2)
    total_horas = models.DecimalField(max_digits=10, decimal_places=2)
    consumo_medio_hora = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    preco_medio_litro = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    gerado_em = models.DateTimeField(auto_now_add=True)
    gerado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['equipamento', 'periodo_inicio', 'periodo_fim']
        verbose_name = 'Relatório de Consumo'
        verbose_name_plural = 'Relatórios de Consumo'

    def __str__(self):
        return f"Relatório {self.equipamento.nome} - {self.periodo_inicio} a {self.periodo_fim}"
