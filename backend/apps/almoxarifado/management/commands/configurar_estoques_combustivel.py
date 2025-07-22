# ----------------------------------------------------------------
# 3. COMANDO PRINCIPAL
# backend/apps/almoxarifado/management/commands/configurar_estoques_combustivel.py
# ----------------------------------------------------------------

from django.core.management.base import BaseCommand
from backend.apps.abastecimento.models import TipoCombustivel
from backend.apps.almoxarifado.models import EstoqueCombustivel, Produto
from decimal import Decimal

class Command(BaseCommand):
    help = 'Configura estoques de combustível no almoxarifado'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--criar-tipos',
            action='store_true',
            help='Criar tipos de combustível padrão'
        )
        parser.add_argument(
            '--estoque-inicial',
            type=float,
            default=1000.0,
            help='Estoque inicial em litros (padrão: 1000L)'
        )
        parser.add_argument(
            '--estoque-minimo',
            type=float,
            default=200.0,
            help='Estoque mínimo em litros (padrão: 200L)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🏪 Configurando estoques de combustível...")
        
        # Criar tipos de combustível se solicitado
        if options['criar_tipos']:
            self._criar_tipos_combustivel()
        
        # Configurar estoques
        self._configurar_estoques(
            estoque_inicial=Decimal(str(options['estoque_inicial'])),
            estoque_minimo=Decimal(str(options['estoque_minimo']))
        )
        
        self.stdout.write(
            self.style.SUCCESS("✅ Configuração de estoques concluída!")
        )
    
    def _criar_tipos_combustivel(self):
        """Cria tipos de combustível padrão"""
        self.stdout.write("⛽ Criando tipos de combustível...")
        
        tipos = [
            ('Diesel S10', 'Diesel S10 para equipamentos pesados', 5.85),
            ('Diesel Comum', 'Diesel comum para equipamentos', 5.45),
            ('Gasolina Comum', 'Gasolina comum para veículos leves', 6.20),
            ('Gasolina Aditivada', 'Gasolina aditivada premium', 6.55),
            ('Arla 32', 'Solução de ureia para SCR', 3.15),
        ]
        
        criados = 0
        for nome, descricao, preco in tipos:
            tipo, created = TipoCombustivel.objects.get_or_create(
                nome=nome,
                defaults={
                    'descricao': descricao,
                    'preco_medio': Decimal(str(preco)),
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(f"  ✅ Criado: {nome}")
                criados += 1
            else:
                self.stdout.write(f"  ⚠️  Já existe: {nome}")
        
        self.stdout.write(f"📊 {criados} tipos de combustível criados\n")
    
    def _configurar_estoques(self, estoque_inicial, estoque_minimo):
        """Configura estoques no almoxarifado"""
        self.stdout.write("📦 Configurando estoques...")
        
        tipos_ativos = TipoCombustivel.objects.filter(ativo=True)
        
        if not tipos_ativos.exists():
            self.stdout.write(
                self.style.WARNING("⚠️ Nenhum tipo de combustível encontrado. Use --criar-tipos")
            )
            return
        
        estoques_criados = 0
        produtos_criados = 0
        
        for tipo in tipos_ativos:
            # Criar ou atualizar estoque
            estoque, created = EstoqueCombustivel.objects.get_or_create(
                tipo_combustivel=tipo,
                defaults={
                    'quantidade_em_estoque': estoque_inicial,
                    'estoque_minimo': estoque_minimo,
                    'valor_compra': tipo.preco_medio,
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(f"  ✅ Estoque criado: {tipo.nome} - {estoque_inicial}L")
                estoques_criados += 1
            else:
                self.stdout.write(f"  📦 Já existe: {tipo.nome} - {estoque.quantidade_em_estoque}L")
            
            # Criar produto correspondente no almoxarifado geral
            produto, prod_created = Produto.objects.get_or_create(
                codigo=f"COMB_{tipo.id}",
                defaults={
                    'descricao': f"Combustível - {tipo.nome}",
                    'unidade_medida': "L",
                    'estoque_atual': estoque_inicial
                }
            )
            
            if prod_created:
                self.stdout.write(f"    📦 Produto criado: {produto.codigo}")
                produtos_criados += 1
            else:
                # Sincronizar estoque do produto com estoque de combustível
                produto.estoque_atual = estoque.quantidade_em_estoque
                produto.save()
                self.stdout.write(f"    🔄 Produto sincronizado: {produto.codigo}")
        
        # Resumo
        self.stdout.write(f"\n📊 RESUMO:")
        self.stdout.write(f"  📦 Estoques criados: {estoques_criados}")
        self.stdout.write(f"  🏷️  Produtos criados: {produtos_criados}")
        self.stdout.write(f"  ⛽ Total de combustíveis: {tipos_ativos.count()}")
        
        # Mostrar status dos estoques
        self.stdout.write(f"\n📋 STATUS DOS ESTOQUES:")
        for estoque in EstoqueCombustivel.objects.filter(ativo=True).select_related('tipo_combustivel'):
            status = "🚨 BAIXO" if estoque.abaixo_do_minimo else "✅ OK"
            self.stdout.write(
                f"  {status} {estoque.tipo_combustivel.nome}: "
                f"{estoque.quantidade_em_estoque}L (mín: {estoque.estoque_minimo}L)"
            )