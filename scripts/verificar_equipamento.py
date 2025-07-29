# scripts/verificar_equipamento.py

import os
import sys
import django

# Configurar Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.equipamentos.models import Equipamento

print("🔧 VERIFICANDO MODELO EQUIPAMENTO")
print("="*50)

# Listar campos do modelo
print("\n📋 CAMPOS DO MODELO:")
for field in Equipamento._meta.fields:
    print(f"  - {field.name} ({field.get_internal_type()})")

# Verificar equipamentos existentes
print("\n🔧 EQUIPAMENTOS CADASTRADOS:")
equipamentos = Equipamento.objects.all()

if equipamentos.exists():
    for eq in equipamentos[:3]:  # Mostrar até 3
        print(f"\n  ID: {eq.id}")
        
        # Tentar diferentes campos possíveis
        campos_possiveis = [
            'numero_serie', 'numero', 'serie', 'codigo', 
            'identificacao', 'patrimonio', 'placa'
        ]
        
        for campo in campos_possiveis:
            if hasattr(eq, campo):
                valor = getattr(eq, campo)
                if valor:
                    print(f"  {campo}: {valor}")
        
        # Campos que provavelmente existem
        if hasattr(eq, 'modelo'):
            print(f"  Modelo: {eq.modelo}")
        if hasattr(eq, 'fabricante'):
            print(f"  Fabricante: {eq.fabricante}")
        if hasattr(eq, 'ativo_nr12'):
            print(f"  Ativo NR12: {eq.ativo_nr12}")
            
        # Mostrar todos os valores não nulos
        print("\n  Campos com valores:")
        for field in eq._meta.fields:
            valor = getattr(eq, field.name)
            if valor and valor != '' and field.name not in ['id', 'created_at', 'updated_at']:
                print(f"    {field.name}: {valor}")
                
else:
    print("  ❌ Nenhum equipamento cadastrado")
    print("\n  Criando equipamento de teste...")
    
    try:
        # Tentar criar um equipamento básico
        eq = Equipamento.objects.create(
            modelo="Equipamento Teste",
            ativo_nr12=True
        )
        print(f"  ✅ Equipamento criado com ID: {eq.id}")
    except Exception as e:
        print(f"  ❌ Erro ao criar: {e}")
        print("\n  Campos obrigatórios:")
        for field in Equipamento._meta.fields:
            if not field.blank and not field.null and field.name not in ['id', 'created_at', 'updated_at']:
                print(f"    - {field.name}")

print("\n" + "="*50)