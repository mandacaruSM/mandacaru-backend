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
