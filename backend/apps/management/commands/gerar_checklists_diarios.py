from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado

class Command(BaseCommand):
    help = 'Gera checklists diários automaticamente para equipamentos ativos'

    def handle(self, *args, **options):
        hoje = date.today()
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        
        if not equipamentos.exists():
            self.stdout.write('❌ Nenhum equipamento ativo encontrado')
            return

        checklists_criados = 0

        for equipamento in equipamentos:
            self.stdout.write(f"📋 Processando: {equipamento.nome}")
            
            # Criar checklist para manhã se não existir
            checklist_existente = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje,
                turno='MANHA'
            ).first()

            if not checklist_existente:
                checklist = ChecklistNR12.objects.create(
                    equipamento=equipamento,
                    data_checklist=hoje,
                    turno='MANHA'
                )
                checklists_criados += 1
                self.stdout.write(f"   ✅ Criado: MANHA (UUID: {checklist.uuid})")
                self.stdout.write(f"   🔗 URL: /api/nr12/checklist/{checklist.uuid}/")
            else:
                self.stdout.write(f"   ⚠️ Já existe: MANHA (UUID: {checklist_existente.uuid})")

        self.stdout.write("\n" + "="*50)
        self.stdout.write(f'✅ RESUMO: {checklists_criados} checklists criados para {hoje}')