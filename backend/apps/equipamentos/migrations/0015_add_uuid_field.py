from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('equipamentos', '0014_corrigir_frequencia_checklist'),  # ← ajuste aqui
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='equipamento',
                    name='uuid',
                    field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
            ],
        ),
    ]
