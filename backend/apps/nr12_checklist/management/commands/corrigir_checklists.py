# ===============================================
# ARQUIVO: backend/apps/nr12_checklist/management/commands/corrigir_checklists.py
# Comando para corrigir problemas específicos dos checklists
# ===============================================

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige problemas específicos identificados nos checklists'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--criar-itens',
            action='store_true',
            help='Criar itens para checklists vazios'
        )
        parser.add_argument(
            '--atribuir-responsavel',
            action='store_true',
            help='Atribuir responsável para checklists órfãos'
        )
        parser.add_argument(
            '--limpar-antigos',
            action='store_true',
            help='Marcar checklists antigos como expirados'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Executar todas as correções'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 CORREÇÃO DE CHECKLISTS')
        )
        self.stdout.write('=' * 40)
        
        try:
            with transaction.atomic():
                if options['criar_itens'] or options['all']:
                    self._criar_itens_checklists()
                
                if options['atribuir_responsavel'] or options['all']:
                    self._atribuir_responsavel_orfaos()
                
                if options['limpar_antigos'] or options['all']:
                    self._limpar_checklists_antigos()
                
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Correções concluídas com sucesso!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante correção: {e}')
            )
    
    def _criar_itens_checklists(self):
        """Cria itens para checklists vazios"""
        self.stdout.write('\n📝 Criando itens para checklists vazios...')
        
        from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado, ItemChecklistPadrao
        from django.db import models
        
        # Buscar checklists sem itens
        checklists_vazios = ChecklistNR12.objects.annotate(
            itens_count=models.Count('itens')
        ).filter(itens_count=0)
        
        self.stdout.write(f'   🔍 Encontrados {checklists_vazios.count()} checklists vazios')
        
        corrigidos = 0
        for checklist in checklists_vazios:
            try:
                # Verificar se equipamento tem tipo NR12
                if not checklist.equipamento.tipo_nr12:
                    self.stdout.write(f'   ⚠️ Checklist {checklist.id}: equipamento sem tipo NR12')
                    continue
                
                # Buscar itens padrão para este tipo
                itens_padrao = ItemChecklistPadrao.objects.filter(
                    tipo_equipamento=checklist.equipamento.tipo_nr12,
                    ativo=True
                ).order_by('ordem')
                
                if not itens_padrao.exists():
                    self.stdout.write(f'   ⚠️ Checklist {checklist.id}: tipo {checklist.equipamento.tipo_nr12.nome} sem itens padrão')
                    continue
                
                # Criar itens
                itens_criados = 0
                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        status='PENDENTE'
                    )
                    itens_criados += 1
                
                self.stdout.write(f'   ✅ Checklist {checklist.id}: {itens_criados} itens criados')
                corrigidos += 1
                
            except Exception as e:
                self.stdout.write(f'   ❌ Erro no checklist {checklist.id}: {e}')
        
        self.stdout.write(f'   📊 Total corrigido: {corrigidos} checklists')
    
    def _atribuir_responsavel_orfaos(self):
        """Atribui responsável para checklists órfãos - CORRIGIDO"""
        self.stdout.write('\n👤 Atribuindo responsável para checklists órfãos...')
        
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from backend.apps.operadores.models import Operador
        from django.contrib.auth import get_user_model
        
        # Usar o modelo User correto do sistema
        User = get_user_model()
        
        # Buscar checklists órfãos
        checklists_orfaos = ChecklistNR12.objects.filter(
            status='EM_ANDAMENTO',
            responsavel__isnull=True
        )
        
        self.stdout.write(f'   🔍 Encontrados {checklists_orfaos.count()} checklists órfãos')
        
        if checklists_orfaos.count() == 0:
            self.stdout.write('   ✅ Nenhum checklist órfão encontrado')
            return
        
        # Buscar usuários disponíveis
        usuarios_disponiveis = User.objects.filter(is_active=True)
        
        if not usuarios_disponiveis.exists():
            self.stdout.write('   ❌ Nenhum usuário ativo encontrado')
            return
        
        # Usar primeiro usuário ativo
        usuario_padrao = usuarios_disponiveis.first()
        
        # Atribuir responsável
        checklists_atualizados = checklists_orfaos.update(responsavel=usuario_padrao)
        
        self.stdout.write(f'   ✅ {checklists_atualizados} checklists atribuídos ao usuário {usuario_padrao.username}')
    
    def _limpar_checklists_antigos(self):
        """Marca checklists antigos como expirados"""
        self.stdout.write('\n📅 Limpando checklists antigos...')
        
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        # Data limite (7 dias atrás)
        data_limite = date.today() - timedelta(days=7)
        
        # Buscar checklists antigos pendentes
        checklists_antigos = ChecklistNR12.objects.filter(
            status='PENDENTE',
            data_checklist__lt=data_limite
        )
        
        self.stdout.write(f'   🔍 Encontrados {checklists_antigos.count()} checklists pendentes antigos')
        
        # Opções de correção
        self.stdout.write('   📋 Escolha uma ação:')
        self.stdout.write('   1. Marcar como EXPIRADO')
        self.stdout.write('   2. Atualizar data para hoje')
        self.stdout.write('   3. Deletar checklists antigos')
        
        # Para comando automático, vamos marcar como expirado
        # Se o status EXPIRADO não existir, podemos usar CANCELADO
        
        try:
            # Tentar atualizar status (assumindo que existe status EXPIRADO ou similar)
            checklists_atualizados = checklists_antigos.update(status='CANCELADO')
            self.stdout.write(f'   ✅ {checklists_atualizados} checklists marcados como CANCELADO')
            
        except Exception as e:
            self.stdout.write(f'   ⚠️ Não foi possível atualizar status: {e}')
            self.stdout.write('   💡 Considere adicionar status EXPIRADO ao modelo')


# ===============================================
# COMANDO PARA VERIFICAR CAMPOS DOS MODELOS
# ===============================================

class VerificarCamposCommand(BaseCommand):
    """Comando auxiliar para verificar campos dos modelos"""
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 VERIFICANDO CAMPOS DOS MODELOS\n')
        
        # Verificar modelo Operador
        from backend.apps.operadores.models import Operador
        self.stdout.write('👤 MODELO OPERADOR:')
        campos_operador = [field.name for field in Operador._meta.get_fields()]
        for campo in sorted(campos_operador):
            self.stdout.write(f'   • {campo}')
        
        # Verificar modelo Equipamento
        from backend.apps.equipamentos.models import Equipamento
        self.stdout.write('\n🔧 MODELO EQUIPAMENTO:')
        campos_equipamento = [field.name for field in Equipamento._meta.get_fields()]
        for campo in sorted(campos_equipamento):
            self.stdout.write(f'   • {campo}')
        
        # Verificar campos específicos
        campos_qr = ['qr_code', 'qr_code_data']
        self.stdout.write('\n🔲 CAMPOS QR:')
        
        for modelo_nome, modelo in [('Operador', Operador), ('Equipamento', Equipamento)]:
            campos_modelo = [field.name for field in modelo._meta.get_fields()]
            self.stdout.write(f'   {modelo_nome}:')
            for campo_qr in campos_qr:
                existe = campo_qr in campos_modelo
                status = '✅' if existe else '❌'
                self.stdout.write(f'     {status} {campo_qr}')