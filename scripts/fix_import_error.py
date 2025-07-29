#!/usr/bin/env python3
"""
🔧 SCRIPT PARA CORRIGIR ERRO DE IMPORT
Execute: python fix_import_error.py
"""

import os
from pathlib import Path

def print_step(step, description):
    print(f"\n{'='*50}")
    print(f"PASSO {step}: {description}")
    print('='*50)

def fix_operadores_urls_bot():
    """Corrige o arquivo urls_bot.py do app operadores"""
    print_step(1, "CORRIGINDO urls_bot.py do app operadores")
    
    urls_bot_path = Path("backend/apps/operadores/urls_bot.py")
    
    # Conteúdo correto do arquivo
    correct_content = '''from django.urls import path
from . import views_bot

app_name = 'operadores_bot'

urlpatterns = [
    path('operador/login/', views_bot.operador_login_bot, name='operador_login_bot'),
    path('operador/<int:operador_id>/validar/', views_bot.validar_operador_bot, name='validar_operador_bot'),
    path('operadores/', views_bot.listar_operadores_bot, name='listar_operadores_bot'),
]
'''
    
    try:
        with open(urls_bot_path, 'w', encoding='utf-8') as f:
            f.write(correct_content)
        print(f"✅ Arquivo corrigido: {urls_bot_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo: {e}")
        return False

def create_operadores_views_bot():
    """Cria o arquivo views_bot.py do app operadores"""
    print_step(2, "CRIANDO views_bot.py do app operadores")
    
    views_bot_path = Path("backend/apps/operadores/views_bot.py")
    
    views_content = '''from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
import logging
from .models import Operador
from datetime import datetime

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def operador_login_bot(request):
    """Login específico para bot telegram"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({
                'success': False, 
                'error': 'Nome é obrigatório'
            })
        
        # Buscar operador por nome (case insensitive, busca parcial)
        operadores = Operador.objects.filter(
            nome__icontains=nome,
            status='ATIVO'  # Apenas operadores ativos
        ).values(
            'id', 
            'nome', 
            'data_nascimento', 
            'chat_id_telegram',
            'cargo',
            'setor'
        )
        
        if not operadores.exists():
            return JsonResponse({
                'success': False, 
                'error': 'Operador não encontrado'
            })
        
        # Converter data de nascimento para string se necessário
        resultado = []
        for op in operadores:
            operador_dict = dict(op)
            if operador_dict['data_nascimento']:
                operador_dict['data_nascimento'] = operador_dict['data_nascimento'].strftime('%Y-%m-%d')
            resultado.append(operador_dict)
        
        return JsonResponse({
            'success': True,
            'operadores': resultado
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        })
    except Exception as e:
        logger.error(f"Erro no login do bot: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@csrf_exempt  
@require_http_methods(["POST"])
def validar_operador_bot(request, operador_id):
    """Validar data de nascimento do operador"""
    try:
        data = json.loads(request.body)
        data_nascimento = data.get('data_nascimento')
        chat_id = data.get('chat_id')
        
        if not data_nascimento:
            return JsonResponse({
                'success': False,
                'error': 'Data de nascimento é obrigatória'
            })
        
        try:
            operador = Operador.objects.get(id=operador_id, status='ATIVO')
        except Operador.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Operador não encontrado'
            })
        
        # Normalizar data de nascimento para comparação  
        data_fornecida = normalizar_data_nascimento(data_nascimento)
        data_operador = operador.data_nascimento.strftime('%Y-%m-%d') if operador.data_nascimento else None
        
        if data_operador and data_fornecida == data_operador:
            # Atualizar chat_id se fornecido
            if chat_id:
                operador.chat_id_telegram = chat_id
                operador.save(update_fields=['chat_id_telegram'])
            
            return JsonResponse({
                'success': True,
                'operador': {
                    'id': operador.id,
                    'nome': operador.nome,
                    'cargo': operador.cargo,
                    'setor': operador.setor,
                    'codigo': getattr(operador, 'codigo', f'OP{operador.id:04d}')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Data de nascimento incorreta'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        })
    except Exception as e:
        logger.error(f"Erro na validação do operador: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def listar_operadores_bot(request):
    """Lista operadores para o bot"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        operadores = Operador.objects.filter(status='ATIVO')
        
        if search:
            operadores = operadores.filter(nome__icontains=search)
        
        paginator = Paginator(operadores, page_size)
        page_obj = paginator.get_page(page)
        
        # Serializar dados
        results = []
        for operador in page_obj:
            results.append({
                'id': operador.id,
                'nome': operador.nome,
                'cargo': operador.cargo,
                'setor': operador.setor,
                'codigo': getattr(operador, 'codigo', f'OP{operador.id:04d}'),
                'data_nascimento': operador.data_nascimento.strftime('%Y-%m-%d') if operador.data_nascimento else None,
                'chat_id_telegram': operador.chat_id_telegram
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar operadores: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

def normalizar_data_nascimento(data_str):
    """Normaliza data para formato YYYY-MM-DD"""
    if not data_str:
        return None
    
    data_str = data_str.strip()
    
    # Se já está no formato correto
    if len(data_str) == 10 and data_str[4] == '-':
        return data_str
    
    # Se está no formato DD/MM/YYYY
    if len(data_str) == 10 and '/' in data_str:
        partes = data_str.split('/')
        if len(partes) == 3:
            dia, mes, ano = partes
            return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
    
    return None
'''
    
    try:
        with open(views_bot_path, 'w', encoding='utf-8') as f:
            f.write(views_content)
        print(f"✅ Arquivo criado: {views_bot_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")
        return False

def create_equipamentos_urls_bot():
    """Cria o arquivo urls_bot.py do app equipamentos"""
    print_step(3, "CRIANDO urls_bot.py do app equipamentos")
    
    # Verificar se o diretório existe
    equipamentos_dir = Path("backend/apps/equipamentos")
    if not equipamentos_dir.exists():
        print(f"⚠️ Diretório não encontrado: {equipamentos_dir}")
        return False
    
    urls_bot_path = equipamentos_dir / "urls_bot.py"
    
    urls_content = '''from django.urls import path
from . import views_bot

app_name = 'equipamentos_bot'

urlpatterns = [
    path('equipamento/<int:equipamento_id>/', views_bot.equipamento_action_bot, name='equipamento_action_bot'),
]
'''
    
    try:
        with open(urls_bot_path, 'w', encoding='utf-8') as f:
            f.write(urls_content)
        print(f"✅ Arquivo criado: {urls_bot_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")
        return False

def create_equipamentos_views_bot():
    """Cria o arquivo views_bot.py do app equipamentos"""
    print_step(4, "CRIANDO views_bot.py do app equipamentos")
    
    equipamentos_dir = Path("backend/apps/equipamentos")
    if not equipamentos_dir.exists():
        print(f"⚠️ Diretório não encontrado: {equipamentos_dir}")
        return False
    
    views_bot_path = equipamentos_dir / "views_bot.py"
    
    views_content = '''from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Equipamento

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def equipamento_action_bot(request, equipamento_id):
    """Actions do equipamento para o bot"""
    try:
        equipamento = Equipamento.objects.get(id=equipamento_id)
        
        if request.method == 'GET':
            # Retornar dados do equipamento
            return JsonResponse({
                'success': True,
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                    'categoria': equipamento.categoria.nome if equipamento.categoria else '',
                    'localizacao': getattr(equipamento, 'localizacao_atual', ''),
                    'status': 'ativo' if getattr(equipamento, 'ativo_nr12', True) else 'inativo'
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            acao = data.get('acao')
            
            if acao == 'iniciar_checklist':
                return processar_iniciar_checklist(equipamento, data)
            elif acao == 'continuar_checklist':
                return processar_continuar_checklist(equipamento, data)
            elif acao == 'status':
                return obter_status_equipamento(equipamento)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Ação "{acao}" não reconhecida'
                })
        
    except Equipamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Equipamento não encontrado'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        })
    except Exception as e:
        logger.error(f"Erro na ação do equipamento: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

def processar_iniciar_checklist(equipamento, data):
    """Processa início de checklist"""
    try:
        operador_id = data.get('operador_id')
        if not operador_id:
            return JsonResponse({
                'success': False,
                'error': 'ID do operador é obrigatório'
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Checklist iniciado com sucesso',
            'checklist': {
                'equipamento': equipamento.nome,
                'status': 'em_andamento'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao iniciar checklist: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao iniciar checklist: {str(e)}'
        })

def processar_continuar_checklist(equipamento, data):
    """Processa continuação de checklist"""
    return JsonResponse({
        'success': True,
        'message': 'Checklist continuado'
    })

def obter_status_equipamento(equipamento):
    """Obtém status detalhado do equipamento"""
    try:
        status_info = {
            'equipamento': {
                'id': equipamento.id,
                'nome': equipamento.nome,
                'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                'categoria': equipamento.categoria.nome if equipamento.categoria else '',
                'localizacao': getattr(equipamento, 'localizacao_atual', ''),
                'ativo': getattr(equipamento, 'ativo_nr12', True)
            }
        }
        
        return JsonResponse({
            'success': True,
            'status': status_info
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter status: {str(e)}'
        })
'''
    
    try:
        with open(views_bot_path, 'w', encoding='utf-8') as f:
            f.write(views_content)
        print(f"✅ Arquivo criado: {views_bot_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")
        return False

def update_main_urls():
    """Atualiza o arquivo principal de URLs"""
    print_step(5, "ATUALIZANDO backend/urls.py")
    
    urls_files = [
        Path("backend/urls.py"),
        Path("backend/config/urls.py"),
        Path("config/urls.py")
    ]
    
    urls_file = None
    for file_path in urls_files:
        if file_path.exists():
            urls_file = file_path
            break
    
    if not urls_file:
        print("❌ Arquivo de URLs principais não encontrado")
        return False
    
    try:
        # Ler arquivo atual
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem as URLs do bot configuradas corretamente
        if "include('backend.apps.operadores.urls_bot')" in content and "include('backend.apps.equipamentos.urls_bot')" in content:
            print("✅ URLs do bot já estão configuradas corretamente")
            return True
        
        # Remover linha problemática se existir
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Pular linha que importa Equipamento incorretamente
            if "path('bot/', include('backend.apps.operadores.urls_bot'))," in line and "Equipamento" in content:
                # Substituir por versões corretas
                new_lines.append("    # URLs para Bot Telegram")
                new_lines.append("    path('bot/', include('backend.apps.operadores.urls_bot')),")
                new_lines.append("    path('bot/', include('backend.apps.equipamentos.urls_bot')),")
            elif "path('bot/'," not in line or "urls_bot" not in line:
                new_lines.append(line)
        
        # Se não encontrou onde adicionar, adicionar no final do urlpatterns
        new_content = '\n'.join(new_lines)
        
        if "include('backend.apps.operadores.urls_bot')" not in new_content:
            # Encontrar onde adicionar
            if 'urlpatterns = [' in new_content:
                lines = new_content.split('\n')
                for i, line in enumerate(lines):
                    if 'urlpatterns = [' in line:
                        # Adicionar após a linha
                        lines.insert(i + 1, "    # URLs para Bot Telegram")
                        lines.insert(i + 2, "    path('bot/', include('backend.apps.operadores.urls_bot')),")
                        lines.insert(i + 3, "    path('bot/', include('backend.apps.equipamentos.urls_bot')),")
                        break
                
                new_content = '\n'.join(lines)
        
        # Backup do arquivo original
        backup_file = urls_file.with_suffix('.py.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Backup criado: {backup_file}")
        
        # Escrever novo conteúdo
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ URLs atualizadas em: {urls_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar URLs: {e}")
        return False

def verify_django_project():
    """Verifica se estamos no diretório correto"""
    if not Path("manage.py").exists():
        print("❌ Arquivo manage.py não encontrado!")
        print("   Execute este script na raiz do projeto Django")
        return False
    
    print("✅ Projeto Django detectado")
    return True

def main():
    """Executa todas as correções"""
    print("🔧 CORREÇÃO AUTOMÁTICA DO ERRO DE IMPORT")
    print("Este script irá corrigir o erro: cannot import name 'Equipamento'")
    
    # Verificar se estamos no local correto
    if not verify_django_project():
        return
    
    print(f"\n📍 Diretório atual: {Path.cwd()}")
    
    # Aplicar correções
    success_count = 0
    total_steps = 5
    
    if fix_operadores_urls_bot():
        success_count += 1
    
    if create_operadores_views_bot():
        success_count += 1
    
    if create_equipamentos_urls_bot():
        success_count += 1
    
    if create_equipamentos_views_bot():
        success_count += 1
    
    if update_main_urls():
        success_count += 1
    
    # Resultado final
    print(f"\n{'='*60}")
    print(f"🎯 RESULTADO: {success_count}/{total_steps} correções aplicadas")
    print('='*60)
    
    if success_count == total_steps:
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python manage.py makemigrations")
        print("2. Execute: python manage.py migrate") 
        print("3. Execute: python manage.py runserver")
        print("4. Em outro terminal: python manage.py run_telegram_bot --debug")
        
        print("\n🧪 TESTE A CORREÇÃO:")
        print("curl -X POST http://127.0.0.1:8000/bot/operador/login/ \\")
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"nome":"admin"}\'')
        
    else:
        print("⚠️ ALGUMAS CORREÇÕES FALHARAM")
        print("   Verifique os erros acima e corrija manualmente")
    
    print(f"\n🔍 ARQUIVOS CRIADOS/MODIFICADOS:")
    print("   • backend/apps/operadores/urls_bot.py")
    print("   • backend/apps/operadores/views_bot.py")
    print("   • backend/apps/equipamentos/urls_bot.py")
    print("   • backend/apps/equipamentos/views_bot.py")
    print("   • backend/urls.py (atualizado)")

if __name__ == "__main__":
    main()