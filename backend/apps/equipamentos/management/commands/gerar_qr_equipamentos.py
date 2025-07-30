# ===============================================
# 2. COMMAND PARA GERAR QR CODES EM MASSA
# ===============================================

# backend/apps/equipamentos/management/commands/gerar_qr_equipamentos.py
from django.core.management.base import BaseCommand
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.qr_generator import gerar_qr_equipamento_para_bot

class Command(BaseCommand):
    help = 'Gera QR codes para todos os equipamentos'

    def add_arguments(self, parser):
        parser.add_argument('--todos', action='store_true', help='Gerar para todos os equipamentos')
        parser.add_argument('--ativos', action='store_true', help='Apenas equipamentos ativos')

    def handle(self, *args, **options):
        # Filtrar equipamentos
        if options['ativos']:
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        elif options['todos']:
            equipamentos = Equipamento.objects.all()
        else:
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)

        total = equipamentos.count()
        self.stdout.write(f"🔄 Gerando QR codes para {total} equipamentos...")
        
        sucessos = 0
        erros = 0

        for equipamento in equipamentos:
            try:
                resultado = gerar_qr_equipamento_para_bot(equipamento)
                self.stdout.write(f"✅ {equipamento}: {resultado['qr_data']}")
                sucessos += 1
            except Exception as e:
                self.stdout.write(f"❌ Erro em {equipamento}: {e}")
                erros += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Concluído! ✅ {sucessos} sucessos, ❌ {erros} erros"))
