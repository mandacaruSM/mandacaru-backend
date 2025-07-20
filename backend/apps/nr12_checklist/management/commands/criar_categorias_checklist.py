# ================================================================
# CRIAR backend/apps/nr12_checklist/management/commands/criar_categorias_checklist.py
# ================================================================
# Executar com: python manage.py criar_categorias_checklist

from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import CategoriaChecklistNR12

class Command(BaseCommand):
    help = 'Cria categorias padrão para Checklist NR12'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Criando categorias de Checklist NR12...\n')
        
        categorias = [
            {
                'codigo': 'ESC',
                'nome': 'Escavadeira',
                'descricao': 'Checklist para escavadeiras hidráulicas'
            },
            {
                'codigo': 'RET', 
                'nome': 'Retroescavadeira',
                'descricao': 'Checklist para retroescavadeiras com carregadeira'
            },
            {
                'codigo': 'CAR',
                'nome': 'Carregadeira', 
                'descricao': 'Checklist para carregadeiras frontais'
            },
            {
                'codigo': 'NIV',
                'nome': 'Motoniveladora',
                'descricao': 'Checklist para motoniveladoras'
            },
            {
                'codigo': 'MOT',
                'nome': 'Motocicleta',
                'descricao': 'Checklist de segurança para motos'
            },
            {
                'codigo': 'TRA',
                'nome': 'Trator de Esteira',
                'descricao': 'Checklist para tratores e esteiras'
            },
            {
                'codigo': 'CAM',
                'nome': 'Caminhão',
                'descricao': 'Checklist para caminhões de transporte'
            },
            {
                'codigo': 'GER',
                'nome': 'Gerador',
                'descricao': 'Checklist para geradores a diesel ou gasolina'
            },
            {
                'codigo': 'OUT',
                'nome': 'Outros',
                'descricao': 'Checklist genérico para outros equipamentos'
            },
            {
                'codigo': 'AUT',
                'nome': 'Veículo',
                'descricao': 'Checklist para veículos de transporte'
            },
            {
                'codigo': 'FIO',
                'nome': 'Máquina de Fio',
                'descricao': 'Checklist para máquinas de corte com fio diamantado'
            },
            {
                'codigo': 'CPA',
                'nome': 'Compressor de Ar',
                'descricao': 'Checklist para compressores de ar'
            }
        ]
        
        criadas = 0
        for cat_data in categorias:
            categoria, created = CategoriaChecklistNR12.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults={
                    'nome': cat_data['nome'],
                    'descricao': cat_data['descricao']
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Criada: {categoria.codigo} - {categoria.nome}')
                criadas += 1
            else:
                self.stdout.write(f'  ⚠️ Já existe: {categoria.codigo} - {categoria.nome}')
        
        self.stdout.write(f'\n🎯 {criadas} categorias de checklist criadas com sucesso!')
        self.stdout.write('📋 Agora você pode vincular equipamentos a categorias de checklist!')
