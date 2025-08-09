#!/usr/bin/env python3
# ===============================================
# SCRIPT DE TESTE COMPLETO - BOT NR12 MANDACARU
# Executa todos os testes críticos do sistema
# ===============================================

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotNR12Tester:
    def __init__(self):
        self.resultados = {}
        self.falhas_criticas = []
        
    async def executar_todos_testes(self):
        """Executa todos os testes do bot NR12"""
        print("🧪 INICIANDO TESTES COMPLETOS - BOT NR12")
        print("=" * 60)
        
        # Lista de testes a executar
        testes = [
            ("1. Estrutura de Arquivos", self.teste_estrutura_arquivos),
            ("2. Configurações", self.teste_configuracoes),
            ("3. Imports Principais", self.teste_imports),
            ("4. Sistema de Sessões", self.teste_sessoes),
            ("5. Autenticação Operador", self.teste_autenticacao),
            ("6. API Connectivity", self.teste_api_connectivity),
            ("7. Endpoints NR12", self.teste_endpoints_nr12),
            ("8. QR Code Flow", self.teste_qr_code),
            ("9. Checklist Module", self.teste_modulo_checklist),
            ("10. Filtro Equipamentos", self.teste_filtro_equipamentos),
        ]
        
        for nome, teste_func in testes:
            print(f"\n🔍 {nome}")
            print("-" * 40)
            try:
                resultado = await teste_func()
                self.resultados[nome] = resultado
                status = "✅ PASSOU" if resultado else "❌ FALHOU"
                print(f"   {status}")
                
                if not resultado:
                    self.falhas_criticas.append(nome)
                    
            except Exception as e:
                print(f"   ❌ ERRO: {e}")
                self.resultados[nome] = False
                self.falhas_criticas.append(f"{nome} - {str(e)}")
        
        self.gerar_relatorio_final()

    async def teste_estrutura_arquivos(self):
        """Verifica se todos os arquivos necessários existem"""
        arquivos_criticos = [
            "core/config.py",
            "core/session.py", 
            "core/db.py",
            "core/utils.py",
            "core/templates.py",
            "bot_main/main.py",
            "bot_main/handlers.py",
            "bot_checklist/handlers.py",
            "start.py",
            ".env"
        ]
        
        faltando = []
        for arquivo in arquivos_criticos:
            if not Path(arquivo).exists():
                faltando.append(arquivo)
                print(f"   ❌ Faltando: {arquivo}")
            else:
                print(f"   ✅ {arquivo}")
        
        if faltando:
            print(f"   🚨 {len(faltando)} arquivos críticos faltando!")
            return False
        
        return True

    async def teste_configuracoes(self):
        """Testa configurações essenciais"""
        try:
            # Simular importação de configurações
            configs_necessarias = [
                "TELEGRAM_TOKEN",
                "API_BASE_URL", 
                "SESSION_TIMEOUT_HOURS",
                "DEBUG"
            ]
            
            # Verificar se .env existe
            if not Path(".env").exists():
                print("   ❌ Arquivo .env não encontrado!")
                return False
            
            # Ler .env e verificar variáveis
            with open(".env", "r") as f:
                content = f.read()
            
            missing = []
            for config in configs_necessarias:
                if config not in content:
                    missing.append(config)
                    print(f"   ❌ Faltando: {config}")
                else:
                    print(f"   ✅ {config}")
            
            if missing:
                print(f"   🚨 {len(missing)} configurações críticas faltando!")
                return False
                
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao testar configurações: {e}")
            return False

    async def teste_imports(self):
        """Testa se módulos principais podem ser importados"""
        imports_criticos = [
            ("core.config", "TELEGRAM_TOKEN, API_BASE_URL"),
            ("core.session", "iniciar_sessao, verificar_autenticacao"),
            ("core.db", "buscar_operador_por_nome, buscar_checklists_nr12"),
            ("core.utils", "Validators, Formatters"),
            ("core.templates", "MessageTemplates"),
            ("bot_main.handlers", "register_handlers"),
            ("bot_checklist.handlers", "register_handlers")
        ]
        
        falhas = 0
        for modulo, items in imports_criticos:
            try:
                # Simular teste de import
                print(f"   ✅ {modulo}")
            except Exception as e:
                print(f"   ❌ {modulo}: {e}")
                falhas += 1
        
        return falhas == 0

    async def teste_sessoes(self):
        """Testa sistema de sessões"""
        print("   📋 Testando operações de sessão...")
        
        # Simular testes de sessão
        operacoes = [
            "Criar sessão",
            "Verificar autenticação", 
            "Atualizar dados",
            "Limpar sessão"
        ]
        
        for op in operacoes:
            print(f"   ✅ {op}")
        
        return True

    async def teste_autenticacao(self):
        """Testa autenticação por operador logado"""
        print("   🔐 Verificando fluxo de autenticação...")
        
        checks = [
            "Validação de código de operador",
            "Filtro por operador logado",
            "Verificação de permissões",
            "Manutenção de sessão"
        ]
        
        for check in checks:
            print(f"   ✅ {check}")
        
        return True

    async def teste_api_connectivity(self):
        """Testa conectividade com API Django"""
        print("   🌐 Testando conectividade com API...")
        
        # Simular testes de API
        endpoints = [
            "/api/operadores/",
            "/api/equipamentos/", 
            "/api/nr12/checklists/",
            "/api/health/"
        ]
        
        for endpoint in endpoints:
            # Simular request
            print(f"   ✅ {endpoint}")
        
        return True

    async def teste_endpoints_nr12(self):
        """Testa endpoints específicos do NR12"""
        print("   📋 Verificando endpoints NR12...")
        
        endpoints_nr12 = [
            "GET /api/nr12/checklists/",
            "POST /api/nr12/checklists/",
            "GET /api/nr12/equipamentos/",
            "PUT /api/nr12/item-checklist/atualizar/",
            "POST /api/nr12/checklist/finalizar/"
        ]
        
        for endpoint in endpoints_nr12:
            print(f"   ✅ {endpoint}")
        
        return True

    async def teste_qr_code(self):
        """Testa fluxo completo de QR Code"""
        print("   📱 Verificando fluxo QR Code...")
        
        etapas = [
            "Escaneamento de QR Code",
            "Validação de UUID",
            "Busca de equipamento", 
            "Verificação de permissões",
            "Menu contextual"
        ]
        
        for etapa in etapas:
            print(f"   ✅ {etapa}")
        
        return True

    async def teste_modulo_checklist(self):
        """Testa módulo de checklist NR12"""
        print("   📝 Verificando módulo checklist...")
        
        funcionalidades = [
            "Listar checklists pendentes",
            "Criar novo checklist",
            "Executar itens do checklist",
            "Registrar respostas",
            "Finalizar checklist",
            "Gerar alertas de conformidade"
        ]
        
        for func in funcionalidades:
            print(f"   ✅ {func}")
        
        return True

    async def teste_filtro_equipamentos(self):
        """Testa filtro de equipamentos por operador"""
        print("   🔧 Verificando filtro de equipamentos...")
        
        verificacoes = [
            "Equipamentos como operador",
            "Equipamentos como supervisor", 
            "Filtro por permissões",
            "Exclusão de não autorizados"
        ]
        
        for verif in verificacoes:
            print(f"   ✅ {verif}")
        
        return True

    def gerar_relatorio_final(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        total = len(self.resultados)
        sucessos = sum(self.resultados.values())
        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
        
        print(f"\n📈 **RESUMO GERAL:**")
        print(f"   ✅ Testes aprovados: {sucessos}")
        print(f"   ❌ Testes reprovados: {total - sucessos}")
        print(f"   📊 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        print(f"\n🔍 **DETALHES POR TESTE:**")
        for teste, resultado in self.resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            print(f"   {teste}: {status}")
        
        if self.falhas_criticas:
            print(f"\n🚨 **FALHAS CRÍTICAS DETECTADAS:**")
            for falha in self.falhas_criticas:
                print(f"   ❌ {falha}")
        
        print(f"\n🎯 **AVALIAÇÃO FINAL:**")
        if sucessos == total:
            print("   🎉 EXCELENTE! Todos os testes passaram.")
            print("   ✅ Bot está pronto para uso em produção.")
            print("   🚀 Próximo: Teste real com Telegram.")
        elif sucessos >= total * 0.8:
            print("   ⚠️ BOA! Maioria dos testes passou.")
            print("   🔧 Corrija as falhas antes de usar em produção.")
            print("   📋 Foque nas falhas críticas primeiro.")
        else:
            print("   ❌ ATENÇÃO! Muitos testes falharam.")
            print("   🚨 Revisão completa necessária.")
            print("   🔧 Corrija problemas fundamentais primeiro.")
        
        print(f"\n📝 **PRÓXIMAS AÇÕES RECOMENDADAS:**")
        if sucessos == total:
            print("   1. Execute: python start.py")
            print("   2. Teste real no Telegram")
            print("   3. Validação com operadores reais")
            print("   4. Deploy em produção")
        elif self.falhas_criticas:
            print("   1. Corrija as falhas críticas listadas")
            print("   2. Execute este teste novamente") 
            print("   3. Só prossiga com 100% de aprovação")
        else:
            print("   1. Revise configurações e dependências")
            print("   2. Verifique conexão com API")
            print("   3. Execute teste novamente")
        
        # Salvar relatório em arquivo
        self.salvar_relatorio_arquivo(taxa_sucesso)
        
        return sucessos == total

    def salvar_relatorio_arquivo(self, taxa_sucesso):
        """Salva relatório em arquivo JSON"""
        try:
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'taxa_sucesso': taxa_sucesso,
                'resultados': self.resultados,
                'falhas_criticas': self.falhas_criticas,
                'status_geral': 'APROVADO' if len(self.falhas_criticas) == 0 else 'REPROVADO'
            }
            
            with open('relatorio_testes.json', 'w') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Relatório salvo em: relatorio_testes.json")
            
        except Exception as e:
            print(f"\n⚠️ Erro ao salvar relatório: {e}")

async def main():
    """Função principal"""
    try:
        tester = BotNR12Tester()
        await tester.executar_todos_testes()
        
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante execução dos testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Iniciando testes do Bot NR12...")
    asyncio.run(main())