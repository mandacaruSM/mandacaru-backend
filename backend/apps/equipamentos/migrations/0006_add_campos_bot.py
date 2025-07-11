# backend/apps/equipamentos/migrations/0006_add_campos_bot.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('nr12_checklist', '0001_initial'),
        ('equipamentos', '0005_equipamento_tipo_nr12_equipamento_updated_at_and_more'),
    ]

    operations = [
        # Adicionar campo codigo se não existir
        migrations.AddField(
            model_name='equipamento',
            name='codigo',
            field=models.CharField(
                blank=True, 
                max_length=50, 
                null=True, 
                unique=True, 
                verbose_name='Código'
            ),
        ),
        
        # Adicionar campo localizacao se não existir  
        migrations.AddField(
            model_name='equipamento',
            name='localizacao',
            field=models.CharField(
                blank=True, 
                max_length=200, 
                null=True, 
                verbose_name='Localização'
            ),
        ),
    ]