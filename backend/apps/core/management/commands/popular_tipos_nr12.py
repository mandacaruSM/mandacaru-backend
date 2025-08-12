import logging
from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import TipoEquipamentoNR12, ItemChecklistPadrao

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cria tipos de equipamentos e itens NR12 padrão'

    def handle(self, *args, **options):
        escavadeira, created = TipoEquipamentoNR12.objects.get_or_create(
            nome='Escavadeira Hidráulica',
            defaults={'descricao': 'Escavadeiras hidráulicas sobre esteiras ou pneus'}
        )
        if created:
            itens_escavadeira = [
                ("Verificar funcionamento dos controles", "Testar todos os joysticks e comandos", "CRITICA", 1),
                ("Inspeção visual dos cilindros hidráulicos", "Verificar vazamentos e danos", "ALTA", 2),
                ("Verificar nível do óleo hidráulico", "Conferir nível e cor do óleo", "ALTA", 3),
                ("Testar freio de estacionamento", "Verificar se trava corretamente", "CRITICA", 4),
                ("Inspeção das esteiras/pneus", "Verificar desgaste e danos", "MEDIA", 5),
                ("Verificar alarme de ré", "Testar funcionamento do alarme sonoro", "ALTA", 6),
                ("Inspeção da cabine e ROPS", "Verificar integridade estrutural", "CRITICA", 7),
                ("Verificar luzes e sinalização", "Testar faróis, lanternas e giroflex", "MEDIA", 8),
                ("Inspeção geral da máquina", "Verificar fixações, soldas e componentes", "MEDIA", 9),
            ]
            for item, desc, crit, ordem in itens_escavadeira:
                ItemChecklistPadrao.objects.create(
                    tipo_equipamento=escavadeira,
                    item=item,
                    descricao=desc,
                    criticidade=crit,
                    ordem=ordem,
                )

        retro, created = TipoEquipamentoNR12.objects.get_or_create(
            nome='Retroescavadeira',
            defaults={'descricao': 'Retroescavadeiras com carregadeira frontal'}
        )
        if created:
            itens_retro = [
                ("Verificar funcionamento dos pedais", "Testar freio, acelerador e embreagem", "CRITICA", 1),
                ("Inspeção do sistema hidráulico", "Verificar pressão e vazamentos", "ALTA", 2),
                ("Testar comando da lança traseira", "Verificar movimentos de escavação", "ALTA", 3),
                ("Verificar pa carregadeira frontal", "Testar levantamento e inclinação", "ALTA", 4),
                ("Inspeção dos pneus", "Verificar calibragem e desgaste", "MEDIA", 5),
                ("Verificar direção e suspensão", "Testar alinhamento e amortecimento", "ALTA", 6),
                ("Testar alarme de ré", "Verificar funcionamento", "ALTA", 7),
                ("Inspeção da cabine", "Verificar cintos e estrutura", "CRITICA", 8),
            ]
            for item, desc, crit, ordem in itens_retro:
                ItemChecklistPadrao.objects.create(
                    tipo_equipamento=retro,
                    item=item,
                    descricao=desc,
                    criticidade=crit,
                    ordem=ordem,
                )

        carregadeira, created = TipoEquipamentoNR12.objects.get_or_create(
            nome='Carregadeira de Rodas',
            defaults={'descricao': 'Carregadeiras frontais sobre pneus'}
        )
        if created:
            itens_carregadeira = [
                ("Verificar sistema de frenagem", "Testar freio de serviço e estacionamento", "CRITICA", 1),
                ("Inspeção da caçamba", "Verificar soldas e desgaste", "ALTA", 2),
                ("Testar sistema hidráulico", "Verificar pressão e temperatura", "ALTA", 3),
                ("Verificar pneus e pressão", "Conferir calibragem e desgaste", "MEDIA", 4),
                ("Inspeção do motor", "Verificar níveis e vazamentos", "ALTA", 5),
                ("Testar direção", "Verificar folgas e alinhamento", "ALTA", 6),
                ("Verificar iluminação", "Testar faróis de trabalho", "MEDIA", 7),
                ("Inspeção da cabine ROPS", "Verificar estrutura de proteção", "CRITICA", 8),
            ]
            for item, desc, crit, ordem in itens_carregadeira:
                ItemChecklistPadrao.objects.create(
                    tipo_equipamento=carregadeira,
                    item=item,
                    descricao=desc,
                    criticidade=crit,
                    ordem=ordem,
                )

        logger.info('Tipos NR12 e itens de checklist criados com sucesso!')