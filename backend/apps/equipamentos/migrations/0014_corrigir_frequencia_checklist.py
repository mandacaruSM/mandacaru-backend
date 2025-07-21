# ================================================================
# MIGRAÇÃO CRÍTICA PARA CORRIGIR CAMPO DUPLICADO
# backend/apps/equipamentos/migrations/0014_corrigir_frequencia_checklist.py
# ================================================================

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('equipamentos', '0013_remove_equipamento_frequencia_checklist_and_more'),
    ]

    operations = [
        # Esta migração garante que apenas o campo correto existe
        # Se você ainda tem o campo antigo, descomente a operação abaixo:
        
        # migrations.RemoveField(
        #     model_name='equipamento',
        #     name='frequencia_checklist',  # Campo antigo singular
        # ),
        
        # Não precisamos adicionar frequencias_checklist pois já existe da migração 0013
        # Apenas garantimos que está configurado corretamente
    ]

# ================================================================
# SCRIPT DE MIGRAÇÃO DE DADOS (se necessário)
# Execute este script no shell do Django se você tem dados antigos:
# python manage.py shell
# ================================================================

"""
# Execute este código no shell do Django se necessário migrar dados antigos:

from backend.apps.equipamentos.models import Equipamento

# Migrar dados do campo antigo para o novo (se necessário)
equipamentos_sem_frequencia = Equipamento.objects.filter(
    frequencias_checklist__isnull=True
).exclude(
    frequencias_checklist=[]
)

for equipamento in equipamentos_sem_frequencia:
    # Se não tem frequência definida, definir como DIÁRIA por padrão
    if not equipamento.frequencias_checklist:
        equipamento.frequencias_checklist = ['DIARIA']
        equipamento.save(update_fields=['frequencias_checklist'])
        print(f"✅ {equipamento.nome}: frequência definida como DIÁRIA")

print("🎉 Migração de dados concluída!")
"""