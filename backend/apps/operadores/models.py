# ================================================================
# MODELO OPERADOR CORRIGIDO COM MÉTODOS PARA BOT
# backend/apps/operadores/models.py
# ================================================================

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
import uuid
import json


from django.contrib.auth.models import User
from django.utils import timezone


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
    qr_code = models.ImageField(
        upload_to='qr_codes/operadores/', 
        blank=True, 
        null=True,
        verbose_name='QR Code do Operador'
    )
    # Controle
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    qr_code = models.ImageField(
        upload_to='qr_codes/operadores/', 
        blank=True, 
        null=True,
        verbose_name='QR Code do Operador'
    )
    qr_code_data = models.CharField(
        max_length=100, 
        unique=True, 
        editable=False,
        blank=True,
        null=True,
        help_text='Dados únicos para identificação do QR Code'
    )

    # Vínculos com sistema
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

    # Permissões do sistema
    pode_fazer_checklist = models.BooleanField(default=True)
    pode_registrar_abastecimento = models.BooleanField(default=True)
    pode_reportar_anomalia = models.BooleanField(default=True)
    pode_ver_relatorios = models.BooleanField(default=False)

    # Hierarquia
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operadores_supervisionados',
        help_text='Supervisor responsável por este operador'
    )

    # Bot Telegram
    chat_id_telegram = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,  # Adicionar null=True
        # unique=True,  # REMOVER isto!
        help_text="ID do chat do Telegram do operador"
    )
    ativo_bot = models.BooleanField(
        default=True,
        help_text="Se o operador pode usar o bot Telegram"
    )
    ultimo_acesso_bot = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Último acesso via bot Telegram"
    )
    qr_code_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Dados do QR Code do operador"
    )
    # Localização e uso
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
        """Gera código sequencial para operador"""
        ultimo = Operador.objects.filter(codigo__startswith='OP').order_by('codigo').last()
        numero = int(ultimo.codigo[2:]) + 1 if ultimo else 1
        return f"OP{numero:04d}"

    def gerar_qr_code(self):
        """Gera QR code usando o gerenciador unificado padronizado"""
        from backend.apps.shared.qr_manager import UnifiedQRManager
        
        try:
            qr_manager = UnifiedQRManager()
            qr_info = qr_manager.gerar_qr_operador(self, 'medium')
            
            # Atualizar campo com caminho relativo padronizado
            self.qr_code = qr_info['relative_path']
            self.save(update_fields=['qr_code'])
            
            return qr_info
            
        except Exception as e:
            # Fallback para método antigo em caso de erro
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao gerar QR code padronizado para {self.codigo}: {e}")
            
            # Método simplificado de backup
            import qrcode
            import json
            from io import BytesIO
            from django.core.files.base import ContentFile
            
            qr_data = {
                'tipo': 'operador',
                'codigo': self.codigo,
                'nome': self.nome,
                'data': self.qr_code_data
            }
            
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            
            filename = f'op_{self.codigo}_medium.png'
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
            self.save(update_fields=['qr_code'])
            
            return {'filename': filename, 'status': 'fallback'}

    # ✅ MÉTODOS CRÍTICOS PARA BOT

    @classmethod
    def verificar_qr_code(cls, qr_code):
        """Verifica e retorna operador pelo QR code"""
        try:
            # Tentar decodificar JSON do QR
            import json
            try:
                qr_data = json.loads(qr_code)
                if isinstance(qr_data, dict) and 'codigo' in qr_data:
                    return cls.objects.filter(
                        codigo=qr_data['codigo'],
                        status='ATIVO',
                        ativo_bot=True
                    ).first()
            except json.JSONDecodeError:
                pass
            
            # Se não é JSON, buscar direto pelo código
            return cls.objects.filter(
                codigo=qr_code,
                status='ATIVO',
                ativo_bot=True
            ).first()
            
        except Exception:
            return None
    
    def atualizar_ultimo_acesso(self, chat_id=None):
        """Atualiza último acesso do operador via bot"""
        from django.utils import timezone
        self.ultimo_acesso_bot = timezone.now()
        if chat_id:
            self.chat_id_telegram = str(chat_id)
        self.save(update_fields=['ultimo_acesso_bot', 'chat_id_telegram'])
    
    def get_resumo_para_bot(self):
        """Retorna resumo dos dados do operador para o bot"""
        return {
            'id': self.id,  # Certifique-se que está retornando o ID
            'codigo': self.codigo,
            'nome': self.nome,
            'funcao': self.funcao,
            'empresa': self.empresa.nome if hasattr(self, 'empresa') and self.empresa else None,
            'chat_id': self.chat_id_telegram,
            'ativo': self.ativo_bot,
            'permissoes': {
                'checklist': True,
                'abastecimento': getattr(self, 'pode_abastecer', False),
                'ordem_servico': getattr(self, 'pode_criar_os', False),
            }
        }
    
    def atualizar_ultimo_acesso(self, chat_id=None):
        """Atualiza último acesso do operador via bot"""
        self.ultimo_acesso_bot = timezone.now()
        if chat_id:
            self.chat_id_telegram = str(chat_id)
        self.save(update_fields=['ultimo_acesso_bot', 'chat_id_telegram'])
    
    def get_resumo_para_bot(self):
        """Retorna resumo dos dados do operador para o bot"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'funcao': self.funcao,
            'empresa': self.empresa.nome if hasattr(self, 'empresa') and self.empresa else None,
            'chat_id': self.chat_id_telegram,
            'ativo': self.ativo_bot,
            'permissoes': {
                'checklist': True,
                'abastecimento': hasattr(self, 'pode_abastecer') and self.pode_abastecer,
                'ordem_servico': hasattr(self, 'pode_criar_os') and self.pode_criar_os,
            }
        }
    
    def pode_usar_bot(self):
        """Verifica se o operador pode usar o bot"""
        return self.status == 'ATIVO' and self.ativo_bot
    
    def gerar_qr_code_data(self):
        """Gera dados para o QR Code do operador"""
        qr_data = {
            'tipo': 'operador',
            'codigo': self.codigo,
            'id': self.id,
            'nome': self.nome,
            'timestamp': timezone.now().isoformat()
        }
        self.qr_code_data = qr_data
        self.save(update_fields=['qr_code_data'])
        return qr_data
    
    def get_equipamentos_disponiveis(self):
        """Retorna equipamentos que este operador pode usar"""
        from backend.apps.equipamentos.models import Equipamento
        
        if self.equipamentos_autorizados.exists():
            return self.equipamentos_autorizados.filter(ativo_nr12=True)
        elif self.clientes_autorizados.exists():
            return Equipamento.objects.filter(
                cliente__in=self.clientes_autorizados.all(), 
                ativo_nr12=True
            )
        else:
            # Se não tem restrições específicas, pode acessar todos
            return Equipamento.objects.filter(ativo_nr12=True)

    def pode_operar_equipamento(self, equipamento):
        """Verifica se pode operar equipamento específico"""
        if not (self.ativo_bot and self.status == 'ATIVO'):
            return False
        
        equipamentos_disponiveis = self.get_equipamentos_disponiveis()
        return equipamento in equipamentos_disponiveis

    def get_checklists_hoje(self):
        """Retorna checklists pendentes para hoje"""
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date
        
        return ChecklistNR12.objects.filter(
            equipamento__in=self.get_equipamentos_disponiveis(),
            data_checklist=date.today(),
            status__in=['PENDENTE', 'EM_ANDAMENTO']
        )

    def pode_iniciar_checklist(self, checklist_id):
        """Verifica se pode iniciar checklist específico"""
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            checklist = ChecklistNR12.objects.get(id=checklist_id)
            
            return (
                checklist.equipamento in self.get_equipamentos_disponiveis() 
                and checklist.status == 'PENDENTE'
                and self.pode_fazer_checklist
            )
        except ChecklistNR12.DoesNotExist:
            return False

    def pode_finalizar_checklist(self, checklist_id):
        """Verifica se pode finalizar checklist específico"""
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            checklist = ChecklistNR12.objects.get(id=checklist_id)
            
            return (
                checklist.equipamento in self.get_equipamentos_disponiveis()
                and checklist.status == 'EM_ANDAMENTO'
                and self.pode_fazer_checklist
                and (checklist.responsavel == self.user or not checklist.responsavel)
            )
        except ChecklistNR12.DoesNotExist:
            return False

    def atualizar_ultimo_acesso(self, chat_id=None):
        """Atualiza último acesso ao bot"""
        from django.utils import timezone
        self.ultimo_acesso_bot = timezone.now()
        if chat_id and chat_id != self.chat_id_telegram:
            self.chat_id_telegram = str(chat_id)
        self.save(update_fields=['ultimo_acesso_bot', 'chat_id_telegram'])

    def get_resumo_para_bot(self):
        """Retorna resumo do operador para o bot"""
        equipamentos = self.get_equipamentos_disponiveis()
        checklists_hoje = self.get_checklists_hoje()
        
        return {
            'codigo': self.codigo,
            'nome': self.nome,
            'funcao': self.funcao,
            'setor': self.setor,
            'permissoes': {
                'pode_fazer_checklist': self.pode_fazer_checklist,
                'pode_registrar_abastecimento': self.pode_registrar_abastecimento,
                'pode_reportar_anomalia': self.pode_reportar_anomalia,
                'pode_ver_relatorios': self.pode_ver_relatorios,
            },
            'equipamentos_disponiveis': [
                {
                    'id': eq.id,
                    'codigo': eq.codigo,
                    'nome': eq.nome,
                    'status': eq.status_operacional
                } for eq in equipamentos[:10]  # Limitar para não sobrecarregar
            ],
            'checklists_pendentes': checklists_hoje.count(),
            'ultimo_equipamento': {
                'id': self.ultimo_equipamento_usado.id,
                'nome': self.ultimo_equipamento_usado.nome,
                'codigo': self.ultimo_equipamento_usado.codigo
            } if self.ultimo_equipamento_usado else None
        }

    @property
    def idade(self):
        """Calcula idade do operador"""
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    @property
    def tempo_empresa(self):
        """Calcula tempo de empresa"""
        from datetime import date
        fim = self.data_demissao or date.today()
        return f"{fim.year - self.data_admissao.year} anos"

    @property
    def qr_dados_bot(self):
        """Dados do QR code para o bot"""
        return {
            'tipo': 'operador',
            'codigo': self.codigo,
            'nome': self.nome,
            'data': self.qr_code_data
        }