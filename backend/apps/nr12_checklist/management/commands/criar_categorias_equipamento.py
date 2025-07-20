# python manage.py criar_categorias_equipamento


from django.core.management.base import BaseCommand
from backend.apps.equipamentos.models import CategoriaEquipamento

class Command(BaseCommand):
    help = 'Cria categorias padrão para o cadastro de equipamentos'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Criando categorias de Equipamentos...\n')

        categorias = [
            {'codigo': 'ESC', 'nome': 'Escavadeira', 'prefixo': 'ESC'},
            {'codigo': 'CAR', 'nome': 'Carregadeira', 'prefixo': 'CAR'},
            {'codigo': 'NIV', 'nome': 'Motoniveladora', 'prefixo': 'NIV'},
            {'codigo': 'MOT', 'nome': 'Motocicleta', 'prefixo': 'MOT'},
            {'codigo': 'TRA', 'nome': 'Trator de Esteira', 'prefixo': 'TRA'},
            {'codigo': 'CAM', 'nome': 'Caminhão', 'prefixo': 'CAM'},
            {'codigo': 'GER', 'nome': 'Gerador', 'prefixo': 'GER'},
            {'codigo': 'OUT', 'nome': 'Outros', 'prefixo': 'OUT'},
            {'codigo': 'AUT', 'nome': 'Veículo leve', 'prefixo': 'AUT'},
            {'codigo': 'FIO', 'nome': 'Máquina de Fio', 'prefixo': 'FIO'},
            {'codigo': 'CPA', 'nome': 'Compressor de Ar', 'prefixo': 'CPA'},
        ]

        criadas = 0
        for cat in categorias:
            categoria, created = CategoriaEquipamento.objects.get_or_create(
                codigo=cat['codigo'],
                defaults={
                    'nome': cat['nome'],
                    'prefixo_codigo': cat['prefixo'],
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(f'  ✅ Criada: {categoria.codigo} - {categoria.nome}')
                criadas += 1
            else:
                self.stdout.write(f'  ⚠️ Já existe: {categoria.codigo} - {categoria.nome}')

        self.stdout.write(f'\n🎯 {criadas} categorias criadas com sucesso!')
        self.stdout.write('📋 Acesse em: /admin/equipamentos/categoriaequipamento/')
