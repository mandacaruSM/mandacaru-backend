# ===============================================
# COMANDO PARA CORRIGIR UUIDs DOS EQUIPAMENTOS
# CRIAR: backend/apps/equipamentos/management/commands/corrigir_uuids.py
# ===============================================

from django.core.management.base import BaseCommand
from backend.apps.equipamentos.models import Equipamento
import uuid

class Command(BaseCommand):
    help = 'Corrige UUIDs dos equipamentos'

    def handle(self, *args, **options):
        self.stdout.write("🔧 CORRIGINDO UUIDs DOS EQUIPAMENTOS...")
        self.stdout.write("=" * 50)
        
        equipamentos = Equipamento.objects.all()
        corrigidos = 0
        
        for equipamento in equipamentos:
            uuid_original = equipamento.uuid
            
            # Se não tem UUID ou UUID inválido
            if not uuid_original or len(str(uuid_original)) < 32:
                # Gerar novo UUID
                novo_uuid = uuid.uuid4()
                equipamento.uuid = novo_uuid
                equipamento.save()
                
                self.stdout.write(f"✅ {equipamento.nome}")
                self.stdout.write(f"   Antigo: {uuid_original}")
                self.stdout.write(f"   Novo: {novo_uuid}")
                self.stdout.write("")
                corrigidos += 1
            else:
                self.stdout.write(f"✅ {equipamento.nome}: UUID já válido")
        
        self.stdout.write(self.style.SUCCESS(f"🎉 {corrigidos} equipamentos corrigidos!"))
        
        # Listar todos os UUIDs válidos
        self.stdout.write("\n📋 UUIDs VÁLIDOS:")
        for eq in Equipamento.objects.all():
            self.stdout.write(f"   {eq.nome}: {eq.uuid}")

# ===============================================
# SCRIPT SIMPLES PARA VERIFICAR E CORRIGIR
# CRIAR: verificar_uuids.py (na raiz do projeto)
# ===============================================

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.equipamentos.models import Equipamento
import uuid

def verificar_e_corrigir_uuids():
    print("🔍 VERIFICANDO UUIDs DOS EQUIPAMENTOS...")
    print("=" * 50)
    
    equipamentos = Equipamento.objects.all()
    
    if not equipamentos.exists():
        print("❌ Nenhum equipamento encontrado!")
        return
    
    for equipamento in equipamentos:
        print(f"\n📋 Equipamento: {equipamento.nome}")
        print(f"   ID: {equipamento.id}")
        print(f"   UUID atual: {equipamento.uuid}")
        print(f"   Tipo UUID: {type(equipamento.uuid)}")
        print(f"   Tamanho: {len(str(equipamento.uuid)) if equipamento.uuid else 0}")
        
        # Verificar se UUID é válido
        try:
            if equipamento.uuid:
                uuid_obj = uuid.UUID(str(equipamento.uuid))
                print(f"   ✅ UUID válido: {uuid_obj}")
            else:
                print(f"   ❌ UUID nulo - Gerando novo...")
                novo_uuid = uuid.uuid4()
                equipamento.uuid = novo_uuid
                equipamento.save()
                print(f"   ✅ Novo UUID: {novo_uuid}")
        except (ValueError, TypeError) as e:
            print(f"   ❌ UUID inválido: {e}")
            print(f"   🔧 Gerando novo...")
            novo_uuid = uuid.uuid4()
            equipamento.uuid = novo_uuid
            equipamento.save()
            print(f"   ✅ Novo UUID: {novo_uuid}")

if __name__ == "__main__":
    verificar_e_corrigir_uuids()
    print("\n🎉 Verificação concluída!")