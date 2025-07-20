# ================================================================
# CRIAR backend/apps/management/commands/criar_categorias.py
# ================================================================
# python manage.py criar_categorias


from django.core.management.base import BaseCommand
from backend.apps.equipamentos.models import CategoriaEquipamento

class Command(BaseCommand):
    help = 'Cria categorias padrão de equipamentos'

    def handle(self, *args, **options):
        self.stdout.write('🏗️ Criando categorias de equipamentos...\n')
        
        categorias = [
            {
                'codigo': 'ESC',
                'nome': 'Escavadeiras',
                'prefixo': 'ESC',
                'descricao': 'Escavadeiras hidráulicas sobre esteiras e pneus'
            },
            {
                'codigo': 'RET', 
                'nome': 'Retroescavadeiras',
                'prefixo': 'RET',
                'descricao': 'Retroescavadeiras com carregadeira frontal'
            },
            {
                'codigo': 'CAR',
                'nome': 'Carregadeiras', 
                'prefixo': 'CAR',
                'descricao': 'Carregadeiras frontais sobre pneus'
            },
            {
                'codigo': 'NIV',
                'nome': 'Motoniveladoras',
                'prefixo': 'NIV', 
                'descricao': 'Motoniveladoras para terraplanagem'
            },
            {
                'codigo': 'MOT',
                'nome': 'Motocicleta',
                'prefixo': 'MOT',
                'descricao': 'Motocicletas'
            },
            {
                'codigo': 'TRA',
                'nome': 'Tratores',
                'prefixo': 'TRA',
                'descricao': 'Tratores de esteira para terraplenagem'
            },
            {
                'codigo': 'CAM',
                'nome': 'Caminhões',
                'prefixo': 'CAM',
                'descricao': 'Caminhões basculantes e fora de estrada'
            },
            {
                'codigo': 'GER',
                'nome': 'Geradores',
                'prefixo': 'GER',
                'descricao': 'Grupos geradores diesel e gasolina'
            },
            {
                'codigo': 'OUT',
                'nome': 'Outros',
                'prefixo': 'OUT',
                'descricao': 'Outros equipamentos diversos'
            },
            {
                'codigo': 'AUT',
                'nome': 'Veiculos',
                'prefixo': 'VEI',
                'descricao': 'Veiculos de trasporte'
            },
            {
                'codigo': 'FIO',
                'nome': 'Maquina de Fio',
                'prefixo': 'MDF',
                'descricao': 'Maquinas de corte a fio diamantado'
            },
            {
                'codigo': 'CPA',
                'nome': 'Compressor de Ar',
                'prefixo': 'CPA',
                'descricao': 'Compressores de ar a diesel'
            }
        ]
        
        criadas = 0
        for cat_data in categorias:
            categoria, created = CategoriaEquipamento.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults={
                    'nome': cat_data['nome'],
                    'prefixo_codigo': cat_data['prefixo'],
                    'descricao': cat_data['descricao']
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Criada: {categoria.codigo} - {categoria.nome}')
                criadas += 1
            else:
                self.stdout.write(f'  ⚠️ Já existe: {categoria.codigo} - {categoria.nome}')
        
        self.stdout.write(f'\n🎉 {criadas} categorias criadas com sucesso!')
        self.stdout.write('📋 Agora você pode criar equipamentos no admin!')