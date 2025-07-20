#### File: backend/apps/bot_telegram/tests/test_services.py
import inspect
from backend.apps.bot_telegram.services.equipamento_service import get_equipamento_by_id, list_equipamentos_ativos
from backend.apps.bot_telegram.services.operador_service import get_operador_por_codigo, list_operadores_ativos
from backend.apps.bot_telegram.services.checklist_service import get_checklist_do_dia, list_checklists_pendentes
from backend.apps.bot_telegram.services.manutencao_service import get_ultima_manutencao, list_historico


def test_equipamento_services_are_coroutines():
    assert inspect.iscoroutinefunction(get_equipamento_by_id)
    assert inspect.iscoroutinefunction(list_equipamentos_ativos)


def test_operador_services_are_coroutines():
    assert inspect.iscoroutinefunction(get_operador_por_codigo)
    assert inspect.iscoroutinefunction(list_operadores_ativos)


def test_checklist_services_are_coroutines():
    assert inspect.iscoroutinefunction(get_checklist_do_dia)
    assert inspect.iscoroutinefunction(list_checklists_pendentes)


def test_manutencao_services_are_coroutines():
    assert inspect.iscoroutinefunction(get_ultima_manutencao)
    assert inspect.iscoroutinefunction(list_historico)