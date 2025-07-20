from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import FrequenciaChecklist

class Command(BaseCommand):
    help = "Popula a tabela de frequências de checklist com DIÁRIO, SEMANAL, MENSAL"

    def handle(self, *args, **kwargs):
        frequencias = [
            ('DIARIO', 'Diário'),
            ('SEMANAL', 'Semanal'),
            ('MENSAL', 'Mensal'),
        ]
        for codigo, nome in frequencias:
            obj, created = FrequenciaChecklist.objects.get_or_create(codigo=codigo, defaults={'nome': nome})
            if created:
                self.stdout.write(f'✔️ Criado: {codigo} - {nome}')
            else:
                self.stdout.write(f'ℹ️ Já existe: {codigo}')
