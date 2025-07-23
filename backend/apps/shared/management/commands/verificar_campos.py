# backend/apps/shared/management/commands/verificar_campos.py

from django.core.management.base import BaseCommand
from backend.apps.operadores.models import Operador

class Command(BaseCommand):
    help = 'Verifica campos do modelo Operador'

    def handle(self, *args, **options):
        self.stdout.write('🔍 VERIFICANDO CAMPOS DO MODELO OPERADOR\n')
        
        # Listar todos os campos
        campos = [field.name for field in Operador._meta.get_fields()]
        
        self.stdout.write('📋 Campos encontrados:')
        for campo in sorted(campos):
            self.stdout.write(f'   • {campo}')
        
        # Verificar campos específicos
        campos_esperados = ['qr_code', 'qr_code_data', 'codigo', 'nome']
        
        self.stdout.write('\n✅ Verificação de campos críticos:')
        for campo in campos_esperados:
            existe = campo in campos
            status = '✅' if existe else '❌'
            self.stdout.write(f'   {status} {campo}: {"Existe" if existe else "NÃO EXISTE"}')
        
        # Testar operador
        try:
            operador = Operador.objects.first()
            if operador:
                self.stdout.write(f'\n👤 Teste com operador {operador.codigo}:')
                self.stdout.write(f'   • qr_code: {operador.qr_code}')
                self.stdout.write(f'   • qr_code_data: {getattr(operador, "qr_code_data", "CAMPO NÃO EXISTE")}')
            else:
                self.stdout.write('\n⚠️  Nenhum operador encontrado no banco')
        except Exception as e:
            self.stdout.write(f'\n❌ Erro ao testar: {e}')