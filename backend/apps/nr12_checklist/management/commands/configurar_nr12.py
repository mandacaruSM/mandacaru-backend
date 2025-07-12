# ================================================================
# ARQUIVO: backend/apps/nr12_checklist/management/commands/configurar_nr12.py
# ================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.apps.nr12_checklist.models import TipoEquipamentoNR12, ItemChecklistPadrao
from datetime import date

class Command(BaseCommand):
    help = 'Configura dados iniciais para o sistema NR12'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os dados existentes antes de criar novos',
        )
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Cria dados de demonstração',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔧 Configurando sistema NR12...")
        
        if options['reset']:
            self.stdout.write("🗑️ Removendo dados existentes...")
            ItemChecklistPadrao.objects.all().delete()
            TipoEquipamentoNR12.objects.all().delete()
            self.stdout.write("✅ Dados removidos!")
        
        # Criar tipos básicos se não existirem
        self._criar_tipos_basicos()
        
        if options['demo']:
            self._criar_dados_demo()
        
        self._exibir_estatisticas()
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Sistema NR12 configurado com sucesso!"))
    
    def _criar_tipos_basicos(self):
        """Cria tipos básicos de equipamentos NR12"""
        self.stdout.write("\n📋 Criando tipos básicos de equipamentos...")
        
        tipos_basicos = [
            {
                'nome': 'Escavadeira Hidráulica',
                'descricao': 'Escavadeiras hidráulicas sobre esteiras ou pneus para movimentação de terra',
                'itens': [
                    ('Verificar funcionamento dos controles de comando', 'Testar todos os joysticks e comandos hidráulicos', 'CRITICA', 1),
                    ('Inspeção visual dos cilindros hidráulicos', 'Verificar vazamentos, danos e vedações dos cilindros', 'ALTA', 2),
                    ('Verificar nível e condição do óleo hidráulico', 'Conferir nível, cor e contaminação do óleo', 'ALTA', 3),
                    ('Testar freio de estacionamento e bloqueios', 'Verificar se trava corretamente todos os movimentos', 'CRITICA', 4),
                    ('Inspeção das esteiras ou pneus', 'Verificar desgaste, danos e tensionamento', 'MEDIA', 5),
                    ('Verificar alarme de ré e sinalização', 'Testar funcionamento do alarme sonoro e visual', 'ALTA', 6),
                    ('Inspeção da cabine e estrutura ROPS/FOPS', 'Verificar integridade da estrutura de proteção', 'CRITICA', 7),
                    ('Verificar sistema de iluminação', 'Testar faróis, lanternas e sinalizadores', 'MEDIA', 8),
                    ('Inspeção geral da máquina', 'Verificar fixações, soldas e componentes estruturais', 'MEDIA', 9),
                    ('Verificar sistema de arrefecimento', 'Inspecionar radiador, mangueiras e nível', 'ALTA', 10),
                ]
            },
            {
                'nome': 'Retroescavadeira',
                'descricao': 'Retroescavadeiras com carregadeira frontal para escavação e carregamento',
                'itens': [
                    ('Verificar funcionamento dos pedais de comando', 'Testar freio, acelerador, embreagem e comandos', 'CRITICA', 1),
                    ('Inspeção do sistema hidráulico completo', 'Verificar pressão, vazamentos e temperatura', 'ALTA', 2),
                    ('Testar comando da lança traseira', 'Verificar todos os movimentos de escavação', 'ALTA', 3),
                    ('Verificar pá carregadeira frontal', 'Testar levantamento, inclinação e movimentos', 'ALTA', 4),
                    ('Inspeção dos pneus e calibragem', 'Verificar pressão, desgaste e danos', 'MEDIA', 5),
                    ('Verificar sistema de direção', 'Testar alinhamento, folgas e funcionamento', 'ALTA', 6),
                    ('Testar alarme de ré e sinalização', 'Verificar funcionamento dos dispositivos de segurança', 'ALTA', 7),
                    ('Inspeção da cabine e cintos', 'Verificar estrutura de proteção e cintos de segurança', 'CRITICA', 8),
                    ('Verificar estabilizadores (outriggers)', 'Testar funcionamento e vedações', 'ALTA', 9),
                    ('Inspeção do motor e fluidos', 'Verificar níveis de óleo, água e combustível', 'ALTA', 10),
                ]
            },
            {
                'nome': 'Carregadeira de Rodas',
                'descricao': 'Carregadeiras frontais sobre pneus para movimentação de materiais',
                'itens': [
                    ('Verificar sistema de frenagem completo', 'Testar freio de serviço e estacionamento', 'CRITICA', 1),
                    ('Inspeção da caçamba e implementos', 'Verificar soldas, desgaste e fixações', 'ALTA', 2),
                    ('Testar sistema hidráulico', 'Verificar pressão, temperatura e funcionamento', 'ALTA', 3),
                    ('Verificar pneus e sistema de rodagem', 'Conferir calibragem, desgaste e alinhamento', 'MEDIA', 4),
                    ('Inspeção do motor e sistemas auxiliares', 'Verificar níveis, vazamentos e funcionamento', 'ALTA', 5),
                    ('Testar sistema de direção', 'Verificar folgas, alinhamento e assistência', 'ALTA', 6),
                    ('Verificar iluminação e sinalização', 'Testar faróis de trabalho e sinalizadores', 'MEDIA', 7),
                    ('Inspeção da cabine ROPS', 'Verificar estrutura de proteção contra capotamento', 'CRITICA', 8),
                    ('Verificar sistema de transmissão', 'Testar câmbio, diferencial e sistemas', 'ALTA', 9),
                    ('Inspeção de segurança geral', 'Verificar dispositivos e sistemas de proteção', 'ALTA', 10),
                ]
            }
        ]
        
        for tipo_data in tipos_basicos:
            tipo, created = TipoEquipamentoNR12.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={'descricao': tipo_data['descricao']}
            )
            
            if created:
                self.stdout.write(f"  ✅ Criado tipo: {tipo_data['nome']}")
                
                # Criar itens para este tipo
                for item, desc, crit, ordem in tipo_data['itens']:
                    ItemChecklistPadrao.objects.create(
                        tipo_equipamento=tipo,
                        item=item,
                        descricao=desc,
                        criticidade=crit,
                        ordem=ordem,
                        ativo=True
                    )
                
                self.stdout.write(f"    📝 {len(tipo_data['itens'])} itens criados")
            else:
                self.stdout.write(f"  ⚠️  Tipo já existe: {tipo_data['nome']}")
    
    def _criar_dados_demo(self):
        """Cria dados de demonstração"""
        self.stdout.write("\n🎮 Criando dados de demonstração...")
        
        # Aqui você pode adicionar criação de equipamentos de exemplo,
        # checklists de demonstração, etc.
        # Por enquanto, apenas uma mensagem
        self.stdout.write("  ℹ️  Dados de demo podem ser adicionados conforme necessário")
    
    def _exibir_estatisticas(self):
        """Exibe estatísticas do sistema"""
        self.stdout.write("\n📊 ESTATÍSTICAS DO SISTEMA:")
        self.stdout.write("-" * 50)
        
        total_tipos = TipoEquipamentoNR12.objects.count()
        total_itens = ItemChecklistPadrao.objects.count()
        
        self.stdout.write(f"🔧 Tipos de equipamento NR12: {total_tipos}")
        self.stdout.write(f"📋 Itens de checklist padrão: {total_itens}")
        
        # Estatísticas por criticidade
        criticas = ItemChecklistPadrao.objects.filter(criticidade='CRITICA').count()
        altas = ItemChecklistPadrao.objects.filter(criticidade='ALTA').count()
        medias = ItemChecklistPadrao.objects.filter(criticidade='MEDIA').count()
        baixas = ItemChecklistPadrao.objects.filter(criticidade='BAIXA').count()
        
        self.stdout.write(f"\n📈 ITENS POR CRITICIDADE:")
        self.stdout.write(f"  🔴 Críticos: {criticas}")
        self.stdout.write(f"  🟠 Altos: {altas}")
        self.stdout.write(f"  🟡 Médios: {medias}")
        self.stdout.write(f"  🟢 Baixos: {baixas}")
        
        # Estatísticas por tipo
        self.stdout.write(f"\n📋 ITENS POR TIPO:")
        for tipo in TipoEquipamentoNR12.objects.all():
            count = tipo.itens_checklist.count()
            self.stdout.write(f"  {tipo.nome}: {count} itens")


# ================================================================
# ARQUIVO: backend/apps/nr12_checklist/management/