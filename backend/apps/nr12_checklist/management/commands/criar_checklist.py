from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.apps.nr12_checklist.models import TipoEquipamentoNR12, ItemChecklistPadrao

class Command(BaseCommand):
    help = 'Cria checklists NR12 conforme lista específica do cliente'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--remover-antigos',
            action='store_true',
            help='Remove itens antigos antes de criar novos',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("📋 Criando checklists conforme lista específica do cliente...")
        
        # Remove itens antigos se solicitado
        if options['remover_antigos']:
            self.stdout.write("🗑️ Itens antigos removidos")
            ItemChecklistPadrao.objects.all().delete()
            TipoEquipamentoNR12.objects.all().delete()
        
        # Definição dos checklists por tipo de equipamento
        checklists_data = {
            'Carregadeira': [
                ('Verificar nível do óleo do motor', 'Conferir nível e condição do óleo do motor', 'CRITICA', 1),
                ('Verificar nível do óleo hidráulico', 'Conferir nível e cor do óleo hidráulico', 'CRITICA', 2),
                ('Verificar nível do líquido de arrefecimento', 'Conferir nível do radiador e reservatório', 'CRITICA', 3),
                ('Verificar pressão dos pneus', 'Conferir calibragem de todos os pneus', 'CRITICA', 4),
                ('Testar freios de serviço', 'Verificar eficiência dos freios principais', 'CRITICA', 5),
                ('Testar freio de estacionamento', 'Verificar travamento do freio de mão', 'CRITICA', 6),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 7),
                ('Verificar funcionamento dos faróis', 'Testar iluminação frontal e traseira', 'MEDIA', 8),
                ('Verificar funcionamento do sinalizador', 'Testar giroflex e pisca-alerta', 'MEDIA', 9),
                ('Verificar vazamentos visíveis', 'Inspecionar vazamentos de óleo ou fluidos', 'ALTA', 10),
                ('Verificar estado dos pneus', 'Inspecionar desgaste e danos nos pneus', 'ALTA', 11),
                ('Testar movimentos hidráulicos', 'Verificar levantamento e inclinação da caçamba', 'CRITICA', 12),
                ('Verificar cintos de segurança', 'Testar funcionamento e fixação', 'CRITICA', 13),
                ('Verificar nível do óleo do diferencial', 'Conferir óleo do eixo traseiro', 'ALTA', 14),
                ('Verificar nível do óleo da transmissão', 'Conferir óleo da caixa de câmbio', 'ALTA', 15),
                ('Verificar filtro de ar', 'Inspecionar limpeza do filtro', 'ALTA', 16),
                ('Verificar estado das mangueiras', 'Inspecionar mangueiras hidráulicas', 'ALTA', 17),
                ('Verificar fixação dos parafusos', 'Conferir apertos das conexões', 'MEDIA', 18),
                ('Verificar estado das articulações', 'Inspecionar pinos e buchas', 'ALTA', 19),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 20),
                ('Trocar filtro de óleo', 'Substituir filtro do motor', 'CRITICA', 21),
                ('Verificar sistema de refrigeração', 'Inspeção completa do sistema', 'ALTA', 22),
            ],
            
            'Escavadeira': [
                ('Verificar nível do óleo do motor', 'Conferir nível e condição do óleo do motor', 'CRITICA', 1),
                ('Verificar nível do óleo hidráulico', 'Conferir nível e cor do óleo hidráulico', 'CRITICA', 2),
                ('Verificar nível do líquido de arrefecimento', 'Conferir nível do radiador', 'CRITICA', 3),
                ('Testar freios de serviço', 'Verificar sistema de frenagem', 'CRITICA', 4),
                ('Testar freio de estacionamento', 'Verificar travamento', 'CRITICA', 5),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 6),
                ('Verificar funcionamento dos faróis', 'Testar iluminação', 'MEDIA', 7),
                ('Verificar vazamentos visíveis', 'Inspecionar vazamentos', 'ALTA', 8),
                ('Testar movimentos hidráulicos', 'Verificar lança, braço e caçamba', 'CRITICA', 9),
                ('Verificar cintos de segurança', 'Testar funcionamento', 'CRITICA', 10),
                ('Verificar estado das esteiras', 'Inspecionar desgaste das esteiras', 'ALTA', 11),
                ('Verificar tensão das esteiras', 'Conferir tensionamento adequado', 'ALTA', 12),
                ('Verificar filtro de ar', 'Inspecionar limpeza', 'ALTA', 13),
                ('Verificar estado das mangueiras', 'Inspecionar mangueiras hidráulicas', 'ALTA', 14),
                ('Verificar fixação dos parafusos', 'Conferir apertos', 'MEDIA', 15),
                ('Verificar estado dos cilindros', 'Inspecionar cilindros hidráulicos', 'ALTA', 16),
                ('Verificar sistema de rotação', 'Testar giro da superestrutura', 'ALTA', 17),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 18),
                ('Trocar filtro de óleo', 'Substituir filtro', 'CRITICA', 19),
            ],
            
            'Compressor': [
                ('Verificar nível do óleo do compressor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar pressão do ar', 'Conferir pressão de trabalho', 'CRITICA', 2),
                ('Verificar funcionamento da válvula de segurança', 'Testar válvula de alívio', 'CRITICA', 3),
                ('Verificar vazamentos de ar', 'Inspecionar vazamentos no sistema', 'ALTA', 4),
                ('Verificar filtro de ar', 'Inspecionar limpeza do filtro', 'ALTA', 5),
                ('Verificar funcionamento do motor', 'Testar partida e funcionamento', 'CRITICA', 6),
                ('Verificar temperatura de operação', 'Monitorar aquecimento', 'ALTA', 7),
                ('Verificar dreno do reservatório', 'Drenar condensado', 'MEDIA', 8),
                ('Verificar correia do compressor', 'Inspecionar tensão e desgaste', 'ALTA', 9),
                ('Verificar sistema de refrigeração', 'Inspecionar resfriamento', 'ALTA', 10),
                ('Verificar conexões elétricas', 'Inspecionar fiação', 'MEDIA', 11),
                ('Verificar mangueiras e conexões', 'Inspecionar conexões pneumáticas', 'ALTA', 12),
                ('Trocar óleo do compressor', 'Realizar troca conforme programa', 'CRITICA', 13),
                ('Trocar filtro de óleo', 'Substituir filtro', 'ALTA', 14),
            ],
            
            'Gerador': [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar nível do combustível', 'Conferir combustível no tanque', 'CRITICA', 2),
                ('Verificar nível do líquido de arrefecimento', 'Conferir radiador', 'CRITICA', 3),
                ('Testar partida do gerador', 'Verificar funcionamento da partida', 'CRITICA', 4),
                ('Verificar voltagem de saída', 'Medir tensão elétrica', 'CRITICA', 5),
                ('Verificar vazamentos visíveis', 'Inspecionar vazamentos', 'ALTA', 6),
                ('Verificar funcionamento dos instrumentos', 'Testar painel de controle', 'ALTA', 7),
                ('Verificar sistema de escape', 'Inspecionar escapamento', 'MEDIA', 8),
                ('Verificar filtro de ar', 'Inspecionar limpeza', 'ALTA', 9),
                ('Verificar correia do alternador', 'Inspecionar tensão', 'ALTA', 10),
                ('Verificar conexões elétricas', 'Inspecionar terminais', 'ALTA', 11),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 12),
                ('Trocar filtro de óleo', 'Substituir filtro', 'ALTA', 13),
            ],
            
            'Vans e Ônibus': [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar nível do líquido de arrefecimento', 'Conferir radiador', 'CRITICA', 2),
                ('Verificar pressão dos pneus', 'Conferir calibragem', 'CRITICA', 3),
                ('Testar freios', 'Verificar sistema de frenagem', 'CRITICA', 4),
                ('Verificar funcionamento dos faróis', 'Testar iluminação', 'MEDIA', 5),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 6),
                ('Verificar cintos de segurança', 'Testar todos os cintos', 'CRITICA', 7),
                ('Verificar espelhos retrovisores', 'Conferir posicionamento', 'ALTA', 8),
                ('Verificar limpador de para-brisa', 'Testar funcionamento', 'MEDIA', 9),
                ('Verificar nível do óleo do câmbio', 'Conferir óleo da transmissão', 'ALTA', 10),
                ('Verificar sistema de direção', 'Testar direção', 'ALTA', 11),
                ('Verificar suspensão', 'Inspecionar amortecedores', 'ALTA', 12),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 13),
            ],
            
            'Caminhão': [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar nível do líquido de arrefecimento', 'Conferir radiador', 'CRITICA', 2),
                ('Verificar pressão dos pneus', 'Conferir calibragem de todos os pneus', 'CRITICA', 3),
                ('Testar freios', 'Verificar sistema de frenagem', 'CRITICA', 4),
                ('Verificar funcionamento dos faróis', 'Testar iluminação', 'MEDIA', 5),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 6),
                ('Verificar cintos de segurança', 'Testar cintos do motorista', 'CRITICA', 7),
                ('Verificar espelhos retrovisores', 'Conferir posicionamento', 'ALTA', 8),
                ('Verificar sistema de carga', 'Inspecionar carroceria/baú', 'ALTA', 9),
                ('Verificar nível do óleo do câmbio', 'Conferir transmissão', 'ALTA', 10),
                ('Verificar sistema de direção', 'Testar direção', 'ALTA', 11),
                ('Verificar suspensão', 'Inspecionar molas e amortecedores', 'ALTA', 12),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 13),
            ],
            
            'Veículo Leve': [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar nível do líquido de arrefecimento', 'Conferir radiador', 'CRITICA', 2),
                ('Verificar pressão dos pneus', 'Conferir calibragem', 'CRITICA', 3),
                ('Testar freios', 'Verificar sistema de frenagem', 'CRITICA', 4),
                ('Verificar funcionamento dos faróis', 'Testar iluminação', 'MEDIA', 5),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 6),
                ('Verificar cintos de segurança', 'Testar cintos', 'CRITICA', 7),
                ('Verificar espelhos retrovisores', 'Conferir posicionamento', 'ALTA', 8),
                ('Verificar limpador de para-brisa', 'Testar funcionamento', 'MEDIA', 9),
                ('Verificar nível do óleo do câmbio', 'Conferir transmissão', 'ALTA', 10),
                ('Verificar sistema de direção', 'Testar direção', 'ALTA', 11),
                ('Verificar suspensão', 'Inspecionar amortecedores', 'ALTA', 12),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 13),
            ],
            
            'Moto': [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar pressão dos pneus', 'Conferir calibragem', 'CRITICA', 2),
                ('Testar freios', 'Verificar freio dianteiro e traseiro', 'CRITICA', 3),
                ('Verificar funcionamento dos faróis', 'Testar iluminação', 'MEDIA', 4),
                ('Verificar funcionamento da buzina', 'Testar sinal sonoro', 'MEDIA', 5),
                ('Verificar espelhos retrovisores', 'Conferir posicionamento', 'ALTA', 6),
                ('Verificar corrente de transmissão', 'Inspecionar tensão e lubrificação', 'ALTA', 7),
                ('Verificar nível do combustível', 'Conferir combustível', 'MEDIA', 8),
                ('Verificar filtro de ar', 'Inspecionar limpeza', 'ALTA', 9),
                ('Verificar sistema de ignição', 'Testar partida', 'ALTA', 10),
                ('Verificar suspensão', 'Inspecionar amortecedores', 'ALTA', 11),
                ('Verificar sistema elétrico', 'Inspecionar fiação', 'MEDIA', 12),
                ('Trocar óleo do motor', 'Realizar troca conforme programa', 'CRITICA', 13),
            ]
        }
        
        total_itens = 0
        
        # Criar checklists para cada tipo de equipamento
        for nome_tipo, itens in checklists_data.items():
            self.stdout.write(f"✅ Criando: {nome_tipo}")
            
            # Buscar ou criar o tipo de equipamento NR12
            tipo_equipamento, created = TipoEquipamentoNR12.objects.get_or_create(
                nome=nome_tipo,
                defaults={
                    'descricao': f'Equipamento do tipo {nome_tipo} - NR12'
                }
            )
            
            # Criar itens do checklist padrão
            itens_criados = 0
            for item, descricao, criticidade, ordem in itens:
                ItemChecklistPadrao.objects.get_or_create(
                    tipo_equipamento=tipo_equipamento,
                    item=item,
                    defaults={
                        'descricao': descricao,
                        'criticidade': criticidade,
                        'ordem': ordem,
                        'ativo': True
                    }
                )
                itens_criados += 1
            
            self.stdout.write(f"  📝 {itens_criados} itens criados")
            total_itens += itens_criados
        
        # Resumo final
        self.stdout.write("\n🎉 CHECKLISTS CRIADOS CONFORME SUA LISTA!")
        self.stdout.write("=" * 60)
        self.stdout.write("📊 RESUMO DOS CHECKLISTS:")
        self.stdout.write("-" * 40)
        
        for nome_tipo, itens in checklists_data.items():
            self.stdout.write(f"🔧 {nome_tipo:<15} {len(itens)} itens")
        
        self.stdout.write("-" * 40)
        self.stdout.write(f"📋 TOTAL: {total_itens} itens de checklist")
        
        self.stdout.write("\n✅ Características:")
        self.stdout.write("• Organizados por ordem de verificação")
        self.stdout.write("• Itens com descrição detalhada")
        self.stdout.write("• Criticidade apropriada para cada item")
        self.stdout.write("• Compatível com sistema NR12")
        self.stdout.write("• Prontos para gerar checklists e QR Codes")
        
        self.stdout.write("\n🚀 Próximos passos:")
        self.stdout.write("1. Vincular equipamentos aos tipos NR12 no admin")
        self.stdout.write("2. Gerar checklists diários automaticamente")
        self.stdout.write("3. Criar QR Codes para os checklists")
        self.stdout.write("4. Configurar alertas de manutenção")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Comando executado com sucesso!"))
        
        # Estatísticas finais
        total_tipos = TipoEquipamentoNR12.objects.count()
        total_itens_bd = ItemChecklistPadrao.objects.count()
        
        self.stdout.write(f"\n📈 ESTATÍSTICAS FINAIS:")
        self.stdout.write(f"• Tipos de equipamento NR12: {total_tipos}")
        self.stdout.write(f"• Itens de checklist padrão: {total_itens_bd}")
        self.stdout.write(f"• Sistema pronto para operação!")