from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
import uuid

class Operador(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CPF', 'CPF'),
        ('RG', 'RG'),
        ('CNH', 'CNH'),
        ('CTPS', 'Carteira de Trabalho'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('SUSPENSO', 'Suspenso'),
        ('AFASTADO', 'Afastado'),
    ]
    
    # Dados pessoais
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=14, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 
                                 message='CPF deve estar no formato: 000.000.000-00')]
    )
    rg = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    # Endereço
    endereco = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    
    # Dados profissionais
    funcao = models.CharField(max_length=100)
    setor = models.CharField(max_length=100)
    data_admissao = models.DateField()
    data_demissao = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Documentos
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default='CPF')
    numero_documento = models.CharField(max_length=50)
    
    # CNH (se aplicável)
    cnh_numero = models.CharField(max_length=20, blank=True)
    cnh_categoria = models.CharField(max_length=5, blank=True)
    cnh_vencimento = models.DateField(null=True, blank=True)
    
    # Status e controle
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVO')
    observacoes = models.TextField(blank=True)
    
    # QR Code
    qr_code = models.ImageField(upload_to='operadores/qrcodes/', blank=True, null=True)
    qr_code_data = models.CharField(max_length=100, unique=True, editable=False)
    
    # Controle
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # NOVOS CAMPOS - VÍNCULOS COM SISTEMA
    clientes_autorizados = models.ManyToManyField(
        'clientes.Cliente',
        blank=True,
        related_name='operadores_autorizados',
        help_text='Clientes que este operador pode atender'
    )
    empreendimentos_autorizados = models.ManyToManyField(
        'empreendimentos.Empreendimento', 
        blank=True,
        related_name='operadores_autorizados',
        help_text='Empreendimentos onde este operador pode trabalhar'
    )
    equipamentos_autorizados = models.ManyToManyField(
        'equipamentos.Equipamento',
        blank=True, 
        related_name='operadores_autorizados',
        help_text='Equipamentos que este operador pode operar'
    )

    pode_fazer_checklist = models.BooleanField(default=True)
    pode_registrar_abastecimento = models.BooleanField(default=True)
    pode_reportar_anomalia = models.BooleanField(default=True)
    pode_ver_relatorios = models.BooleanField(default=False)

    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operadores_supervisionados',
        help_text='Supervisor responsável por este operador'
    )

    ultimo_acesso_bot = models.DateTimeField(null=True, blank=True)
    chat_id_telegram = models.CharField(max_length=50, blank=True, unique=True)
    ativo_bot = models.BooleanField(default=True, help_text='Pode usar o bot do Telegram')

    localizacao_atual = models.CharField(max_length=200, blank=True)
    ultimo_equipamento_usado = models.ForeignKey(
        'equipamentos.Equipamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ultimo_operador'
    )

    class Meta:
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'
        ordering = ['nome']
        permissions = [
            ('can_use_telegram_bot', 'Pode usar bot do Telegram'),
            ('can_supervise_operators', 'Pode supervisionar operadores'),
            ('can_manage_equipment', 'Pode gerenciar equipamentos'),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.gerar_codigo()
        if not self.qr_code_data:
            self.qr_code_data = f"OP_{self.codigo}_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.gerar_qr_code()

    def gerar_codigo(self):
        ultimo = Operador.objects.filter(codigo__startswith='OP').order_by('codigo').last()
        numero = int(ultimo.codigo[2:]) + 1 if ultimo else 1
        return f"OP{numero:04d}"

    def gerar_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr_data = {'tipo': 'operador', 'codigo': self.codigo, 'nome': self.nome, 'data': self.qr_code_data}
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((250, 250))

        final_img = Image.new('RGB', (300, 350), 'white')
        final_img.paste(qr_img, (25, 25))
        draw = ImageDraw.Draw(final_img)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        draw.text((25, 285), f"{self.codigo}\n{self.nome[:25]}", fill="black", font=font)

        buffer = BytesIO()
        final_img.save(buffer, format='PNG')
        buffer.seek(0)
        self.qr_code.save(f'operador_{self.codigo}_qr.png', File(buffer), save=False)
        self.save(update_fields=['qr_code'])

    @property
    def idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    @property
    def tempo_empresa(self):
        from datetime import date
        fim = self.data_demissao or date.today()
        return f"{fim.year - self.data_admissao.year} anos"

    def get_equipamentos_disponiveis(self):
        from backend.apps.equipamentos.models import Equipamento
        if self.equipamentos_autorizados.exists():
            return self.equipamentos_autorizados.filter(ativo_nr12=True)
        elif self.clientes_autorizados.exists():
            return Equipamento.objects.filter(cliente__in=self.clientes_autorizados.all(), ativo_nr12=True)
        return Equipamento.objects.filter(ativo_nr12=True)

    def pode_operar_equipamento(self, equipamento):
        return self.ativo_bot and self.status == 'ATIVO' and equipamento in self.get_equipamentos_disponiveis()

    def get_checklists_pendentes(self):
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date
        return ChecklistNR12.objects.filter(
            equipamento__in=self.get_equipamentos_disponiveis(),
            data_checklist=date.today(),
            status__in=['PENDENTE', 'EM_ANDAMENTO']
        )

    def atualizar_ultimo_acesso(self, chat_id=None):
        from django.utils import timezone
        self.ultimo_acesso_bot = timezone.now()
        if chat_id:
            self.chat_id_telegram = chat_id
        self.save(update_fields=['ultimo_acesso_bot', 'chat_id_telegram'])
