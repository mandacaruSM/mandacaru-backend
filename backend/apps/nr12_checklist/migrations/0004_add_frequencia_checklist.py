from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Atualize conforme sua última migração
        ('nr12_checklist', '0003_alter_abastecimento_equipamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrequenciaChecklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('nome', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Frequência de Checklist',
                'verbose_name_plural': 'Frequências de Checklists',
                'ordering': ['codigo'],
            },
        ),
    ]
