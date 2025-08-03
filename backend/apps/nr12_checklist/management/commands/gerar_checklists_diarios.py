# ================================================================
# CRIAR ESTE ARQUIVO: backend/apps/nr12_checklist/management/commands/gerar_checklists_diarios.py
# ================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Gera checklists diários NR12 para todos os equipamentos ativos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Data para gerar checklists (formato: YYYY-MM-DD). Padrão: hoje'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força criação mesmo se já existir checklist para a data'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Mostra informações detalhadas de debug'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando geração de checklists diários NR12...")
        
        # Determinar data
        if options['data']:
            try:
                data_checklist = date.fromisoformat(options['data'])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('❌ Formato de data inválido. Use YYYY-MM-DD')
                )
                return
        else:
            data_checklist = date.today()
        
        self.stdout.write(f"📅 Data: {data_checklist}")
        
        try:
            # Importar e executar task
            from backend.apps.core.tasks import gerar_checklists_automatico
            
            # Executar task diretamente (sem Celery)
            resultado = gerar_checklists_automatico()
            
            if isinstance(resultado, dict):
                criados = resultado.get('checklists_criados', 0)
                erros = resultado.get('erros', 0)
                
                if criados > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {criados} checklists criados com sucesso!')
                    )
                
                if erros > 0:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ {erros} erros encontrados')
                    )
                
                if options['debug']:
                    self.stdout.write(f"📊 Resultado completo: {resultado}")
            
            else:
                self.stdout.write(f"✅ Processo concluído: {resultado}")
                
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro de importação: {e}')
            )
            self.stdout.write('💡 Verifique se o arquivo backend/apps/core/tasks.py existe')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na execução: {e}')
            )
            if options['debug']:
                import traceback
                self.stdout.write(traceback.format_exc())
        
        self.stdout.write("🏁 Processo finalizado!")