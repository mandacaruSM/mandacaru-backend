# ================================================================
# TESTE RÁPIDO PARA VERIFICAR SE O SERVIDOR INICIA
# Execute: python teste_servidor_rapido.py
# ================================================================

import subprocess
import time
import requests
import threading
import sys

def testar_servidor():
    """Testa se o servidor Django consegue iniciar"""
    print("🚀 TESTE RÁPIDO: Verificando se servidor Django inicia")
    print("=" * 50)
    
    # Tentar fazer uma requisição rápida para verificar se já está rodando
    try:
        response = requests.get("http://127.0.0.1:8000/api/", timeout=2)
        print("✅ Servidor já está rodando!")
        print(f"📊 Status: {response.status_code}")
        return True
    except:
        print("📋 Servidor não está rodando, continuando teste...")
    
    # Verificar se há problemas de importação
    print("\n🔍 Verificando importações...")
    
    try:
        # Testar importação das URLs principais
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        
        print("✅ Django configurado com sucesso")
        
        # Testar importação do URLs
        from backend.urls import urlpatterns
        print("✅ URLs principais importadas com sucesso")
        
        # Testar importação específica do NR12
        from backend.apps.nr12_checklist.urls import urlpatterns as nr12_urls
        print("✅ URLs do NR12 importadas com sucesso")
        
        # Testar importação dos serializers
        from backend.apps.nr12_checklist.serializers import (
            TipoEquipamentoNR12Serializer,
            ChecklistNR12Serializer,
            ChecklistNR12BotSerializer,
            BotResponseSerializer
        )
        print("✅ Serializers importados com sucesso")
        
        # Testar importação dos viewsets
        from backend.apps.nr12_checklist.viewsets import (
            TipoEquipamentoNR12ViewSet,
            ChecklistNR12ViewSet
        )
        print("✅ ViewSets importados com sucesso")
        
        print("\n🎯 RESULTADO: ✅ TODAS AS IMPORTAÇÕES OK!")
        print("📋 O servidor deve conseguir iniciar normalmente agora.")
        print("\n💡 Execute: python manage.py runserver")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORTAÇÃO:")
        print(f"   {str(e)}")
        print(f"\n🔧 POSSÍVEIS SOLUÇÕES:")
        print(f"   1. Verifique se todos os serializers estão definidos")
        print(f"   2. Confirme se não há imports circulares")
        print(f"   3. Verifique se os nomes dos serializers coincidem")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL:")
        print(f"   {str(e)}")
        return False

if __name__ == "__main__":
    sucesso = testar_servidor()
    if sucesso:
        print("\n🚀 Teste concluído com SUCESSO!")
        sys.exit(0)
    else:
        print("\n❌ Teste FALHOU - verifique os erros acima")
        sys.exit(1)