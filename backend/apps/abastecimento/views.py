from backend.apps.equipamentos.models import Equipamento
from .models import RelatorioConsumo
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime
from decimal import Decimal

@login_required
def gerar_relatorio_consumo_view(request):
    if request.method == 'POST':
        equipamento_id = request.POST.get('equipamento_id')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')

        try:
            equipamento = Equipamento.objects.get(id=equipamento_id)
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

            registros = RegistroAbastecimento.objects.filter(
                equipamento=equipamento,
                data_abastecimento__date__gte=data_inicio,
                data_abastecimento__date__lte=data_fim
            ).order_by('data_abastecimento')

            if not registros.exists():
                return render(request, 'abastecimento/relatorio_resultado.html', {
                    'mensagem': 'Nenhum registro encontrado para o período selecionado.'
                })

            primeira = registros.first()
            ultima = registros.last()
            total_litros = registros.aggregate(models.Sum('quantidade_litros'))['quantidade_litros__sum'] or Decimal('0.00')
            total_valor = registros.aggregate(models.Sum('valor_total'))['valor_total__sum'] or Decimal('0.00')
            total_horas = ultima.medicao_atual - (primeira.medicao_anterior or Decimal('0.00'))
            consumo_medio = total_litros / total_horas if total_horas > 0 else None
            preco_medio = total_valor / total_litros if total_litros > 0 else None

            relatorio = RelatorioConsumo.objects.create(
                equipamento=equipamento,
                periodo_inicio=data_inicio,
                periodo_fim=data_fim,
                total_litros=total_litros,
                total_valor=total_valor,
                total_horas=total_horas,
                consumo_medio_hora=consumo_medio,
                preco_medio_litro=preco_medio,
                gerado_por=request.user
            )

            return render(request, 'abastecimento/relatorio_resultado.html', {
                'relatorio': relatorio
            })

        except Exception as e:
            return render(request, 'abastecimento/relatorio_resultado.html', {
                'mensagem': f'Erro ao gerar relatório: {str(e)}'
            })

    equipamentos = Equipamento.objects.all()
    return render(request, 'abastecimento/relatorio_gerar.html', {'equipamentos': equipamentos})
