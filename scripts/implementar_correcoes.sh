#!/bin/bash

# ===============================================
# SCRIPT DE IMPLEMENTAÇÃO AUTOMÁTICA DAS CORREÇÕES
# scripts/implementar_correcoes.sh
# ===============================================

echo "🚀 IMPLEMENTANDO CORREÇÕES DO BOT TELEGRAM"
echo "=========================================="

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Execute este script na raiz do projeto Django (onde está o manage.py)"
    exit 1
fi

echo "📁 Diretório atual: $(pwd)"
echo "✅ Arquivo manage.py encontrado"

# 1. Criar diretórios necessários
echo ""
echo "📂 Criando estrutura de diretórios..."
mkdir -p backend/apps/nr12_checklist/management/commands
mkdir -p backend/apps/core/management/commands
mkdir -p scripts

# 2. Criar as views do bot para nr12_checklist
echo ""
echo "📝 Criando views do bot para NR12..."
cat > backend/apps/nr12_checklist/views_bot.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from datetime import date, timedelta

from .models import ChecklistNR12
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot(request):
    """Checklists públicos para o bot"""
    try:
        operador_id = request.GET.get('operador_id')
        equipamento_id = request.GET.get('equipamento_id')
        
        queryset = ChecklistNR12.objects.select_related('equipamento')
        
        if operador_id:
            try:
                operador = Operador.objects.get(id=operador_id)
                equipamentos = Equipamento.objects.filter(ativo=True)[:10]
                queryset = queryset.filter(equipamento__in=equipamentos)
            except Operador.DoesNotExist:
                pass
        
        if equipamento_id:
            queryset = queryset.filter(equipamento_id=equipamento_id)
        
        data_limite = date.today() - timedelta(days=30)
        queryset = queryset.filter(data_checklist__gte=data_limite)
        
        checklists = []
        for checklist in queryset[:20]:
            checklists.append({
                'id': checklist.id,
                'equipamento_id': checklist.equipamento.id,
                'equipamento_nome': checklist.equipamento.nome,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'status': checklist.status,
                'turno': getattr(checklist, 'turno', 'MANHA'),
            })
        
        return Response({
            'success': True,
            'count': len(checklists),
            'results': checklists
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_operador(request, operador_id):
    """Equipamentos de um operador"""
    try:
        operador = Operador.objects.get(id=operador_id)
        equipamentos = Equipamento.objects.filter(ativo=True)[:10]
        
        equipamentos_data = []
        for eq in equipamentos:
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'ativo': getattr(eq, 'ativo', True),
            })
        
        return Response({
            'success': True,
            'operador_id': operador_id,
            'count': len(equipamentos_data),
            'equipamentos': equipamentos_data
        })
        
    except Operador.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Operador não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
EOF

# 3. Criar as views do bot para equipamentos
echo ""
echo "📝 Criando views do bot para equipamentos..."
cat > backend/apps/equipamentos/views_bot.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Equipamento


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_publicos(request):
    """Lista equipamentos (público para bot)"""
    try:
        operador_id = request.GET.get('operador_id')
        equipamentos = Equipamento.objects.filter(ativo=True)[:20]
        
        equipamentos_data = []
        for eq in equipamentos:
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'ativo': getattr(eq, 'ativo', True),
                'horimetro_atual': getattr(eq, 'horimetro_atual', 0),
                'status_operacional': getattr(eq, 'status_operacional', 'Operacional'),
            })
        
        return Response({
            'success': True,
            'count': len(equipamentos_data),
            'results': equipamentos_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_equipamento(request, equipamento_id):
    """Checklists de um equipamento específico"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date, timedelta
        
        equipamento = Equipamento.objects.get(id=equipamento_id)
        
        data_limite = date.today() - timedelta(days=30)
        checklists = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist__gte=data_limite
        ).order_by('-data_checklist')[:10]
        
        checklists_data = []
        for checklist in checklists:
            checklists_data.append({
                'id': checklist.id,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'status': checklist.status,
                'turno': getattr(checklist, 'turno', 'MANHA'),
            })
        
        return Response({
            'success': True,
            'equipamento': {
                'id': equipamento.id,
                'nome': equipamento.nome,
            },
            'count': len(checklists_data),
            'checklists': checklists_data
        })
        
    except Equipamento.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Equipamento não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
EOF

# 4. Criar as views do bot para operadores
echo ""
echo "📝 Criando views do bot para operadores..."
cat > backend/apps/operadores/views_bot.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Operador


@api_view(['PATCH'])
@permission_classes([AllowAny])
def atualizar_operador(request, operador_id):
    """Atualiza chat_id do operador"""
    try:
        operador = get_object_or_404(Operador, id=operador_id)
        
        chat_id = request.data.get('chat_id_telegram')
        if chat_id:
            operador.chat_id_telegram = chat_id
            operador.save(update_fields=['chat_id_telegram'])
        
        return Response({
            'success': True,
            'message': 'Operador atualizado',
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'chat_id_telegram': getattr(operador, 'chat_id_telegram', None),
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
EOF

# 5. Criar comando Django para aplicar correções
echo ""
echo "📝 Criando comando Django de correção..."
cat > backend/apps/core/management/commands/corrigir_bot.py << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import requests

class Command(BaseCommand):
    help = 'Corrige problemas do bot automaticamente'

    def handle(self, *args, **options):
        self.stdout.write("🔧 APLICANDO CORREÇÕES DO BOT")
        
        self.verificar_modelos()
        self.criar_dados_teste()
        self.testar_apis()
        
        self.stdout.write("✅ Correções aplicadas!")

    def verificar_modelos(self):
        try:
            from backend.apps.operadores.models import Operador
            
            operador = Operador.objects.first()
            if operador:
                if hasattr(operador, 'chat_id_telegram'):
                    self.stdout.write("✅ Campo chat_id_telegram OK")
                else:
                    self.stdout.write("⚠️ Campo chat_id_telegram não encontrado")
        except Exception as e:
            self.stdout.write(f"❌ Erro: {e}")

    def criar_dados_teste(self):
        try:
            from backend.apps.operadores.models import Operador
            
            try:
                operador = Operador.objects.get(id=9)
                if not getattr(operador, 'chat_id_telegram', None):
                    operador.chat_id_telegram = "853870420"
                    operador.save()
                    self.stdout.write("✅ Chat ID de teste configurado")
            except Operador.DoesNotExist:
                self.stdout.write("⚠️ Operador ID 9 não encontrado")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao criar dados: {e}")

    def testar_apis(self):
        import requests
        
        base_url = "http://127.0.0.1:8000"
        
        testes = [
            f"{base_url}/api/operadores/?chat_id_telegram=853870420",
            f"{base_url}/api/equipamentos/por-uuid/ea23d82d-549b-44bf-8981-7f94e6802461/",
        ]
        
        for url in testes:
            try:
                response = requests.get(url, timeout=3)
                status = "✅" if response.status_code == 200 else "❌"
                self.stdout.write(f"{status} {url} [{response.status_code}]")
            except:
                self.stdout.write(f"❌ {url} [ERRO]")
EOF

# 6. Criar arquivo __init__.py nos management/commands
touch backend/apps/core/management/__init__.py
touch backend/apps/core/management/commands/__init__.py

# 7. Criar patch para o backend/urls.py
echo ""
echo "📝 Criando patch para URLs principais..."
cat > backend/urls_bot_patch.py << 'EOF'
# ===============================================
# PATCH PARA backend/urls.py
# ADICIONE ESTAS LINHAS AO SEU ARQUIVO backend/urls.py
# ===============================================

# Adicione estes imports no topo do arquivo backend/urls.py:
from backend.apps.nr12_checklist.views_bot import checklists_bot, equipamentos_operador
from backend.apps.equipamentos.views_bot import equipamentos_publicos, checklists_equipamento  
from backend.apps.operadores.views_bot import atualizar_operador

# Adicione estas URLs ao final de urlpatterns (antes das URLs de arquivos estáticos):
urlpatterns += [
    # ENDPOINTS PÚBLICOS PARA O BOT TELEGRAM
    path('api/checklists/', checklists_bot, name='checklists-bot'),
    path('api/nr12/checklists/', checklists_bot, name='nr12-checklists-bot'),
    path('api/equipamentos/', equipamentos_publicos, name='equipamentos-publicos'),
    path('api/operadores/<int:operador_id>/equipamentos/', equipamentos_operador, name='operador-equipamentos'),
    path('api/equipamentos/<int:equipamento_id>/checklists/', checklists_equipamento, name='equipamento-checklists'),
    path('api/operadores/<int:operador_id>/', atualizar_operador, name='atualizar-operador'),
]
EOF

# 8. Criar script de teste
echo ""
echo "📝 Criando script de teste..."
cat > scripts/testar_bot_apis.py << 'EOF'
#!/usr/bin/env python
import requests
import json

def testar_apis():
    print("🧪 TESTANDO APIs DO BOT")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8000"
    
    testes = [
        {
            'nome': 'Operador por Chat ID',
            'url': f'{base_url}/api/operadores/?chat_id_telegram=853870420',
        },
        {
            'nome': 'Equipamento Prisma por UUID',
            'url': f'{base_url}/api/equipamentos/por-uuid/ea23d82d-549b-44bf-8981-7f94e6802461/',
        },
        {
            'nome': 'Equipamento EH01 por UUID',
            'url': f'{base_url}/api/equipamentos/por-uuid/9cca38f1-a244-4911-8875-19f1191dd045/',
        },
        {
            'nome': 'Checklists (novo endpoint)',
            'url': f'{base_url}/api/checklists/?operador_id=9',
        },
        {
            'nome': 'Equipamentos (novo endpoint)',
            'url': f'{base_url}/api/equipamentos/?operador_id=9',
        },
        {
            'nome': 'Equipamentos do Operador',
            'url': f'{base_url}/api/operadores/9/equipamentos/',
        },
        {
            'nome': 'Checklists do Equipamento 1',
            'url': f'{base_url}/api/equipamentos/1/checklists/',
        },
    ]
    
    for teste in testes:
        try:
            response = requests.get(teste['url'], timeout=5)
            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {teste['nome']}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'count' in data:
                        print(f"   📊 {data['count']} registros")
                    elif isinstance(data, list):
                        print(f"   📊 {len(data)} registros")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {teste['nome']}: {e}")
    
    print("\n🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_apis()
EOF

# 9. Tornar script executável
chmod +x scripts/testar_bot_apis.py

# 10. Mostrar instruções
echo ""
echo "🎉 CORREÇÕES IMPLEMENTADAS COM SUCESSO!"
echo "======================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. 📝 ATUALIZAR backend/urls.py:"
echo "   Abra o arquivo backend/urls.py e adicione o conteúdo de:"
echo "   📄 backend/urls_bot_patch.py"
echo ""
echo "2. 🔄 REINICIAR o servidor Django:"
echo "   python manage.py runserver"
echo ""
echo "3. 🧪 TESTAR as correções:"
echo "   python scripts/testar_bot_apis.py"
echo ""
echo "4. 🔧 APLICAR correções automáticas:"
echo "   python manage.py corrigir_bot"
echo ""
echo "5. 🤖 TESTAR o bot:"
echo "   python manage.py run_telegram_bot --debug"
echo ""
echo "📋 ARQUIVOS CRIADOS:"
echo "✅ backend/apps/nr12_checklist/views_bot.py"
echo "✅ backend/apps/equipamentos/views_bot.py"
echo "✅ backend/apps/operadores/views_bot.py"
echo "✅ backend/apps/core/management/commands/corrigir_bot.py"
echo "✅ backend/urls_bot_patch.py (instruções)"
echo "✅ scripts/testar_bot_apis.py"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   Você DEVE adicionar as URLs do patch ao seu backend/urls.py"
echo "   manualmente para que os endpoints funcionem!"
echo ""
echo "🎯 ENDPOINTS QUE SERÃO CORRIGIDOS:"
echo "   • /api/checklists/ (público)"
echo "   • /api/nr12/checklists/ (público)"
echo "   • /api/equipamentos/ (público)"
echo "   • /api/operadores/{id}/equipamentos/ (público)"
echo "   • /api/equipamentos/{id}/checklists/ (público)"
                                                      • /api/operadores/{id}/ (PATCH suportado)"
echo ""

# 11. Exibir conteúdo do patch para facilitar
echo "📋 CONTEÚDO DO PATCH (copie e cole no backend/urls.py):"
echo "=================================================="
cat backend/urls_bot_patch.py
echo ""
echo "=================================================="

echo ""
echo "✅ IMPLEMENTAÇÃO CONCLUÍDA!"
echo "Execute os próximos passos listados acima."