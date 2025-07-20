#python manage.py criar_itens_padrao_checklist
from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import CategoriaChecklistNR12, ItemChecklistPadrao

class Command(BaseCommand):
    help = 'Cria os itens padrão de checklist NR12 por categoria'

    def handle(self, *args, **options):
        self.stdout.write('🛠️ Criando itens padrão de Checklist NR12...\n')

        itens_por_categoria = {
            'ESC': [
                'Verificar buzina de advertência',
                'Verificar alarme de ré funcional',
                'Checar sinalização de segurança',
                'Verificar botão de parada de emergência',
                'Verificar cinto de segurança'
            ],
            'CAM': [
                'Checar pneus e rodas',
                'Verificar freios de serviço e estacionamento',
                'Verificar iluminação e setas',
                'Verificar espelhos retrovisores',
                'Verificar cinto de segurança'
            ],
            'CAR': [
                'Verificar controle de basculamento',
                'Verificar estrutura do chassi',
                'Verificar sistema hidráulico de elevação',
                'Checar alarme de ré e buzina'
            ],
            'CPA': [
                'Verificar reservatório de óleo',
                'Checar vazamentos',
                'Verificar filtros e mangueiras',
                'Inspecionar estrutura do compressor'
            ],
            'GER': [
                'Verificar painel elétrico',
                'Checar nível de combustível',
                'Verificar aterramento do equipamento',
                'Checar vibração e ruído'
            ]
        }

        total = 0
        for codigo, itens in itens_por_categoria.items():
            try:
                categoria = CategoriaChecklistNR12.objects.get(codigo=codigo)
            except CategoriaChecklistNR12.DoesNotExist:
                self.stdout.write(f'❌ Categoria {codigo} não encontrada, pulei.')
                continue

            for descricao in itens:
                obj, created = ItemChecklistPadrao.objects.get_or_create(
                    categoria=categoria,
                    descricao=descricao
                )
                if created:
                    total += 1
                    self.stdout.write(f'  ✅ {categoria.nome}: {descricao}')
                else:
                    self.stdout.write(f'  ⚠️ Já existe: {categoria.nome} - {descricao}')

        self.stdout.write(f'\n📋 {total} itens padrão criados com sucesso!')
