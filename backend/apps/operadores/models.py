# backend/apps/operadores/models.py
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid, json
from django.db.models import Q

class Operador(models.Model):
    TIPO_DOCUMENTO_CHOICES = [('CPF','CPF'),('RG','RG'),('CNH','CNH'),('CTPS','Carteira de Trabalho')]
    STATUS_CHOICES = [('ATIVO','Ativo'),('INATIVO','Inativo'),('SUSPENSO','Suspenso'),('AFASTADO','Afastado')]

    # Dados pessoais
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=14, unique=True,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$','CPF no formato 000.000.000-00')]
    )
    rg = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    # Endereço
    endereco = models.CharField(max_length=200)
    cidade   = models.CharField(max_length=100)
    estado   = models.CharField(max_length=2)
    cep      = models.CharField(max_length=10)

    # Dados profissionais
    funcao = models.CharField(max_length=100)
    setor  = models.CharField(max_length=100)
    data_admissao  = models.DateField()
    data_demissao  = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Documentos
    tipo_documento  = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default='CPF')
    numero_documento = models.CharField(max_length=50)

    # CNH
    cnh_numero     = models.CharField(max_length=20, blank=True)
    cnh_categoria  = models.CharField(max_length=5, blank=True)
    cnh_vencimento = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVO')
    observacoes = models.TextField(blank=True)

    # Controle/integração
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # QR Code (campo + payload JSON)
    qr_code = models.ImageField(upload_to='qr_codes/operadores/', blank=True, null=True, verbose_name='QR Code do Operador')
    qr_code_data = models.JSONField(blank=True, null=True, default=dict)

    # Vínculos
    clientes_autorizados       = models.ManyToManyField('clientes.Cliente', blank=True, related_name='operadores_autorizados')
    empreendimentos_autorizados= models.ManyToManyField('empreendimentos.Empreendimento', blank=True, related_name='operadores_autorizados')
    equipamentos_autorizados   = models.ManyToManyField('equipamentos.Equipamento', blank=True, related_name='operadores_autorizados')

    # Permissões
    pode_fazer_checklist        = models.BooleanField(default=True)
    pode_registrar_abastecimento= models.BooleanField(default=True)
    pode_reportar_anomalia      = models.BooleanField(default=True)
    pode_ver_relatorios         = models.BooleanField(default=False)

    # Hierarquia
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='operadores_supervisionados')

    # Bot Telegram
    chat_id_telegram = models.CharField(max_length=50, blank=True, null=True)
    ativo_bot        = models.BooleanField(default=True)
    ultimo_acesso_bot= models.DateTimeField(null=True, blank=True)

    # Localização/uso
    localizacao_atual = models.CharField(max_length=200, blank=True)
    ultimo_equipamento_usado = models.ForeignKey('equipamentos.Equipamento', on_delete=models.SET_NULL,
                                                 null=True, blank=True, related_name='ultimo_operador')

    class Meta:
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'
        ordering = ['nome']
        permissions = [
            ('can_use_telegram_bot','Pode usar bot do Telegram'),
            ('can_supervise_operators','Pode supervisionar operadores'),
            ('can_manage_equipment','Pode gerenciar equipamentos'),
        ]

    def __str__(self): return f"{self.codigo} - {self.nome}"

    # -------- Utilidades --------
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._gerar_codigo()
        if not self.qr_code_data:
            self.qr_code_data = {"tipo":"operador","codigo":self.codigo,"token":f"OP_{self.codigo}_{uuid.uuid4().hex[:8]}"}
        super().save(*args, **kwargs)
        if not self.qr_code:
            self._gerar_qr_code()

    def _gerar_codigo(self):
        ultimo = Operador.objects.filter(codigo__startswith='OP').order_by('codigo').last()
        n = int(ultimo.codigo[2:]) + 1 if ultimo else 1
        return f"OP{n:04d}"

    def _gerar_qr_code(self):
        try:
            from backend.apps.shared.qr_manager import UnifiedQRManager
            info = UnifiedQRManager().gerar_qr_operador(self, 'medium')
            self.qr_code = info['relative_path']
            self.save(update_fields=['qr_code'])
        except Exception:
            import qrcode
            from io import BytesIO
            from django.core.files.base import ContentFile
            data = json.dumps({'tipo':'operador','codigo':self.codigo,'id':self.id,'data':self.qr_code_data})
            img = qrcode.make(data)
            buf = BytesIO(); img.save(buf, format='PNG')
            self.qr_code.save(f'op_{self.codigo}_medium.png', ContentFile(buf.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

    # -------- Bot --------
    @classmethod
    def verificar_qr_code(cls, qr_text:str):
        try:
            data = json.loads(qr_text)
            codigo = data.get('codigo') if isinstance(data, dict) else None
        except json.JSONDecodeError:
            codigo = qr_text
        return cls.objects.filter(codigo=codigo, status='ATIVO', ativo_bot=True).first() if codigo else None

    def atualizar_ultimo_acesso(self, chat_id=None):
        self.ultimo_acesso_bot = timezone.now()
        if chat_id: self.chat_id_telegram = str(chat_id)
        self.save(update_fields=['ultimo_acesso_bot','chat_id_telegram'])

    def pode_usar_bot(self)->bool:
        return self.status=='ATIVO' and self.ativo_bot

    def get_checklists_hoje(self):
        from backend.apps.nr12_checklist.models import ChecklistNR12
        if not self.user_id: return ChecklistNR12.objects.none()
        hoje = timezone.localdate()
        qs = ChecklistNR12.objects.filter(responsavel=self.user, data_checklist=hoje)
        if 'status' in {f.name for f in ChecklistNR12._meta.get_fields()}:
            qs = qs.filter(status__in=['PENDENTE','EM_ANDAMENTO','ABERTO','ABERTA'])
        return qs.order_by('-id')

    def get_checklists_abertos(self):
        from backend.apps.nr12_checklist.models import ChecklistNR12
        status_abertos = ['PENDENTE', 'EM_ANDAMENTO']
        eq_ids = self.get_equipamentos_disponiveis().values_list('pk', flat=True)

        cond = Q(responsavel__isnull=True, equipamento_id__in=eq_ids) | Q(responsavel__operador__supervisor=self)
        if self.user_id:
            cond |= Q(responsavel=self.user)

        return (ChecklistNR12.objects
                .filter(Q(status__in=status_abertos) & cond)
                .order_by('-data_inicio', '-created_at', '-id')
                .distinct())

    def get_equipamentos_disponiveis(self):
        from backend.apps.equipamentos.models import Equipamento
        ids = set()
        if self.equipamentos_autorizados.exists():
            ids.update(self.equipamentos_autorizados.filter(ativo_nr12=True).values_list('id', flat=True))
        if self.clientes_autorizados.exists():  # <- somar fontes
            ids.update(Equipamento.objects.filter(cliente__in=self.clientes_autorizados.all(), ativo_nr12=True)
                       .values_list('id', flat=True))
        if self.operadores_supervisionados.exists():
            for sup in self.operadores_supervisionados.filter(status='ATIVO', ativo_bot=True):
                if sup.equipamentos_autorizados.exists():
                    ids.update(sup.equipamentos_autorizados.filter(ativo_nr12=True).values_list('id', flat=True))
                if sup.clientes_autorizados.exists():
                    ids.update(Equipamento.objects.filter(cliente__in=sup.clientes_autorizados.all(), ativo_nr12=True)
                               .values_list('id', flat=True))
        if not ids and not self.operadores_supervisionados.exists():
            ids.update(Equipamento.objects.filter(ativo_nr12=True).values_list('id', flat=True))
        return Equipamento.objects.filter(id__in=ids, ativo_nr12=True).order_by('nome')

    def pode_iniciar_checklist(self, checklist_id:int)->bool:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        try: c = ChecklistNR12.objects.get(id=checklist_id)
        except ChecklistNR12.DoesNotExist: return False
        if not (self.pode_fazer_checklist and self.pode_usar_bot()): return False
        if getattr(c,'status',None) != 'PENDENTE': return False
        return c.equipamento in self.get_equipamentos_disponiveis()

    def pode_finalizar_checklist(self, checklist_id:int)->bool:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        try: c = ChecklistNR12.objects.get(id=checklist_id)
        except ChecklistNR12.DoesNotExist: return False
        if not (self.pode_fazer_checklist and self.pode_usar_bot()): return False
        if getattr(c,'status',None) != 'EM_ANDAMENTO': return False
        if c.equipamento not in self.get_equipamentos_disponiveis(): return False
        if c.responsavel and c.responsavel != self.user:
            op_resp = getattr(c.responsavel,'operador',None)
            return bool(op_resp and op_resp.supervisor_id==self.id)
        return True

    def get_resumo_para_bot(self):
        equipamentos = self.get_equipamentos_disponiveis()
        supervisionados = []
        if self.operadores_supervisionados.exists():
            for s in self.operadores_supervisionados.filter(status='ATIVO'):
                supervisionados.append({
                    'id': s.id, 'nome': s.nome, 'codigo': s.codigo,
                    'equipamentos_count': s.get_equipamentos_disponiveis().count()
                })
        return {
            'codigo': self.codigo, 'nome': self.nome, 'funcao': self.funcao, 'setor': self.setor,
            'is_supervisor': self.operadores_supervisionados.exists(),
            'supervisor_nome': self.supervisor.nome if self.supervisor else None,
            'supervisionados': supervisionados,
            'permissoes': {
                'pode_fazer_checklist': self.pode_fazer_checklist,
                'pode_registrar_abastecimento': self.pode_registrar_abastecimento,
                'pode_reportar_anomalia': self.pode_reportar_anomalia,
                'pode_ver_relatorios': self.pode_ver_relatorios,
            },
            'equipamentos_disponiveis': [{
                'id': e.id, 'codigo': e.codigo, 'nome': e.nome,
                'status': e.status_operacional,
                'cliente': e.cliente.nome if getattr(e,'cliente',None) else 'N/A'
            } for e in equipamentos[:15]],
            'checklists_pendentes': self.get_checklists_abertos().count(),
            'ultimo_equipamento': (
                {'id': self.ultimo_equipamento_usado.id, 'nome': self.ultimo_equipamento_usado.nome,
                 'codigo': self.ultimo_equipamento_usado.codigo} if self.ultimo_equipamento_usado else None
            ),
            'ultimo_acesso': self.ultimo_acesso_bot.isoformat() if self.ultimo_acesso_bot else None,
        }

    # -------- Propriedades --------
    @property
    def idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - ((hoje.month,hoje.day) < (self.data_nascimento.month,self.data_nascimento.day))

    @property
    def tempo_empresa(self):
        from datetime import date
        fim = self.data_demissao or date.today()
        anos = fim.year - self.data_admissao.year - ((fim.month,fim.day) < (self.data_admissao.month,self.data_admissao.day))
        return f"{anos} anos"
