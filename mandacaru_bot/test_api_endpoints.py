# ===============================================
# ARQUIVO: test_api_endpoints.py
# Script para testar endpoints da API do bot
# ===============================================

import asyncio
import aiohttp
import json
from datetime import date
from typing import Dict, Any, Optional

class APITester:
    """Classe para testar endpoints da API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                          params: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"🔍 Testando {method} {endpoint}")
            if params:
                print(f"   Parâmetros: {params}")
            if data:
                print(f"   Dados: {json.dumps(data, indent=2)}")
            
            async with self.session.request(
                method=method,
                url=url,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=params
            ) as response:
                
                response_data = {}
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "expected_status": expected_status,
                    "success": response.status == expected_status,
                    "response_data": response_data,
                    "params": params,
                    "data": data
                }
                
                if result["success"]:
                    print(f"   ✅ Status: {response.status} (esperado: {expected_status})")
                else:
                    print(f"   ❌ Status: {response.status} (esperado: {expected_status})")
                
                self.test_results.append(result)
                return result
                
        except Exception as e:
            error_result = {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "success": False,
                "params": params,
                "data": data
            }
            print(f"   ❌ Erro: {e}")
            self.test_results.append(error_result)
            return error_result

    async def test_api_root(self):
        """Testa endpoint raiz da API"""
        print("\n📡 TESTANDO API RAIZ")
        print("=" * 50)
        
        return await self.test_endpoint("GET", "/api/")

    async def test_operador_endpoints(self):
        """Testa endpoints relacionados a operadores"""
        print("\n👥 TESTANDO ENDPOINTS DE OPERADORES")
        print("=" * 50)
        
        results = []
        
        # Teste 1: Listar operadores
        results.append(await self.test_endpoint("GET", "/api/operadores/"))
        
        # Teste 2: Equipamentos de operador específico (ID fictício)
        results.append(await self.test_endpoint(
            "GET", 
            "/api/operadores/1/equipamentos/",
            expected_status=200  # Pode retornar 200 mesmo se operador não existir
        ))
        
        # Teste 3: Atualizar operador (sem dados - deve dar erro)
        results.append(await self.test_endpoint(
            "POST", 
            "/api/operadores/1/",
            data={"chat_id": "123456789"},
            expected_status=200
        ))
        
        return results

    async def test_checklist_endpoints(self):
        """Testa endpoints de checklists"""
        print("\n📋 TESTANDO ENDPOINTS DE CHECKLISTS")
        print("=" * 50)
        
        results = []
        
        # Teste 1: Listar checklists sem filtro
        results.append(await self.test_endpoint("GET", "/api/nr12/checklists/"))
        
        # Teste 2: Listar checklists com filtro de operador
        results.append(await self.test_endpoint(
            "GET", 
            "/api/nr12/checklists/",
            params={"operador_id": 1, "status": "PENDENTE"}
        ))
        
        # Teste 3: Listar checklists com data específica
        results.append(await self.test_endpoint(
            "GET", 
            "/api/nr12/checklists/",
            params={
                "operador_id": 1, 
                "data_checklist": date.today().isoformat()
            }
        ))
        
        # Teste 4: Endpoint alternativo de checklists
        results.append(await self.test_endpoint("GET", "/api/checklists/"))
        
        return results

    async def test_equipamento_endpoints(self):
        """Testa endpoints de equipamentos"""
        print("\n🔧 TESTANDO ENDPOINTS DE EQUIPAMENTOS")
        print("=" * 50)
        
        results = []
        
        # Teste 1: Listar equipamentos públicos
        results.append(await self.test_endpoint("GET", "/api/equipamentos/"))
        
        # Teste 2: Equipamentos com filtro de operador
        results.append(await self.test_endpoint(
            "GET", 
            "/api/equipamentos/",
            params={"operador_id": 1}
        ))
        
        # Teste 3: Checklists de equipamento específico
        results.append(await self.test_endpoint(
            "GET", 
            "/api/equipamentos/1/checklists/"
        ))
        
        return results

    async def test_bot_specific_endpoints(self):
        """Testa endpoints específicos do bot"""
        print("\n🤖 TESTANDO ENDPOINTS ESPECÍFICOS DO BOT")
        print("=" * 50)
        
        results = []
        
        # Teste 1: Login de operador via bot
        results.append(await self.test_endpoint(
            "POST", 
            "/api/nr12/bot/operador/login/",
            data={
                "codigo": "OP001",
                "data_nascimento": "1990-01-01"
            },
            expected_status=200
        ))
        
        # Teste 2: Acesso a equipamento via bot
        results.append(await self.test_endpoint(
            "GET", 
            "/api/nr12/bot/equipamento/1/"
        ))
        
        # Teste 3: Atualizar item de checklist
        results.append(await self.test_endpoint(
            "POST", 
            "/api/nr12/bot/item-checklist/atualizar/",
            data={
                "item_id": 1,
                "status": "OK",
                "observacao": "Teste de funcionamento",
                "operador_codigo": "OP001"
            }
        ))
        
        return results

    async def test_pagination_and_filters(self):
        """Testa paginação e filtros"""
        print("\n📄 TESTANDO PAGINAÇÃO E FILTROS")
        print("=" * 50)
        
        results = []
        
        # Teste 1: Paginação de checklists
        results.append(await self.test_endpoint(
            "GET", 
            "/api/nr12/checklists/",
            params={"page": 1, "page_size": 5}
        ))
        
        # Teste 2: Filtros múltiplos
        results.append(await self.test_endpoint(
            "GET", 
            "/api/nr12/checklists/",
            params={
                "operador_id": 1,
                "status": "PENDENTE",
                "equipamento_id": 1,
                "page": 1
            }
        ))
        
        return results

    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Total de testes: {total_tests}")
        print(f"✅ Sucessos: {successful_tests}")
        print(f"❌ Falhas: {failed_tests}")
        print(f"📊 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ TESTES FALHARAM:")
            for result in self.test_results:
                if not result.get("success", False):
                    endpoint = result.get("endpoint", "N/A")
                    method = result.get("method", "N/A")
                    error = result.get("error", "Status code mismatch")
                    print(f"   • {method} {endpoint}: {error}")
        
        print("\n" + "=" * 60)

    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES DOS ENDPOINTS DA API")
        print("=" * 60)
        
        try:
            # Testar API raiz
            await self.test_api_root()
            
            # Testar endpoints principais
            await self.test_operador_endpoints()
            await self.test_checklist_endpoints()
            await self.test_equipamento_endpoints()
            
            # Testar endpoints específicos do bot
            await self.test_bot_specific_endpoints()
            
            # Testar paginação e filtros
            await self.test_pagination_and_filters()
            
        except Exception as e:
            print(f"❌ Erro crítico durante testes: {e}")
        
        finally:
            self.print_summary()

# ===============================================
# FUNÇÃO PRINCIPAL PARA EXECUTAR TESTES
# ===============================================

async def main():
    """Função principal para executar os testes"""
    
    # Configurar URL base da API
    API_BASE_URL = "http://127.0.0.1:8000"  # Ajustar conforme necessário
    
    async with APITester(API_BASE_URL) as tester:
        await tester.run_all_tests()

# ===============================================
# SCRIPT ADICIONAL PARA TESTAR FILTROS ESPECÍFICOS
# ===============================================

async def test_supervisor_filters():
    """Testa filtros específicos para supervisores"""
    print("\n👑 TESTANDO FILTROS DE SUPERVISOR")
    print("=" * 50)
    
    async with APITester() as tester:
        # Teste com operador supervisor
        await tester.test_endpoint(
            "GET",
            "/api/operadores/3/equipamentos/",  # ID 3 = supervisor conforme setup
            params={"include_supervisionados": True}
        )
        
        # Teste checklists de equipe
        await tester.test_endpoint(
            "GET",
            "/api/nr12/checklists/",
            params={
                "operador_id": 3,
                "include_team": True,
                "status": "PENDENTE"
            }
        )

# ===============================================
# EXECUTAR SE CHAMADO DIRETAMENTE
# ===============================================

if __name__ == "__main__":
    print("🧪 TESTADOR DE ENDPOINTS DA API - MANDACARU BOT")
    print("Certifique-se de que o servidor Django está rodando!")
    print("Pressione Ctrl+C para interromper os testes")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")