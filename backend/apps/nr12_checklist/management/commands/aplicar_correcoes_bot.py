# ===============================================
# CORREÇÃO 6: Comando para aplicar as correções
# backend/apps/nr12_checklist/management/commands/aplicar_correcoes_bot.py
# ===============================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import requests

class Command(BaseCommand):
    help = 'Aplica correções nos endpoints do bot e testa'
    
    def handle(self, *args, **options):
        self.stdout.write("🔧 APLICANDO CORREÇÕES DO BOT")
        self.stdout.write("=" * 40)
        
        # 1. Verificar se models têm os campos necessários
        self.verificar_models()
        
        # 2. Testar novos endpoints
        self.testar_endpoints()
        
        # 3. Criar dados de teste se necessário
        self.criar_dados_teste()
        
        self.stdout.write("\n✅ CORREÇÕES APLICADAS!")
    
    def verificar_models(self):
        self.stdout.write("\n📋 Verificando models...")
        
        try:
            from backend.apps.operadores.models import Operador
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12
            
            # Verificar campo chat_id_telegram
            operador = Operador.objects.first()
            if operador and hasattr(operador, 'chat_id_telegram'):
                self.stdout.write("✅ Campo chat_id_telegram existe")
            else:
                self.stdout.write("⚠️ Campo chat_id_telegram não encontrado")
            
            # Verificar UUID em equipamentos
            equipamento = Equipamento.objects.first()
            if equipamento and hasattr(equipamento, 'uuid'):
                self.stdout.write("✅ Campo UUID em equipamentos existe")
            else:
                self.stdout.write("⚠️ Campo UUID em equipamentos não encontrado")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao verificar models: {e}")
    
    def testar_endpoints(self):
        self.stdout.write("\n🌐 Testando novos endpoints...")
        
        base_url = "http://127.0.0.1:8000"
        
        endpoints = [
            f"{base_url}/api/nr12/bot/checklists/",
            f"{base_url}/api/operadores/por-chat-id/?chat_id=853870420",
            f"{base_url}/api/equipamentos/publico/",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                status = "✅" if response.status_code < 400 else "❌"
                self.stdout.write(f"{status} {endpoint} [{response.status_code}]")
            except Exception as e:
                self.stdout.write(f"❌ {endpoint} [ERROR: {e}]")
    
    def criar_dados_teste(self):
        self.stdout.write("\n🔧 Criando dados de teste...")
        
        try:
            from backend.apps.operadores.models import Operador
            
            # Atualizar operador com chat_id de teste
            operador = Operador.objects.filter(id=9).first()
            if operador:
                operador.chat_id_telegram = "853870420"
                operador.save()
                self.stdout.write("✅ Chat ID de teste configurado")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao criar dados de teste: {e}")
