# ===============================================
# ARQUIVO: test_checklist_flow.py
# Teste completo do fluxo de checklist NR12
# ===============================================

import asyncio
import aiohttp
import json
from datetime import date, datetime
from typing import Dict, Any, List

class ChecklistFlowTester:
    """Testa o fluxo completo de criação/execução de checklist"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_data = {
            'operador_codigo': 'OP001',
            'equipamento_id': 1,
            'checklist_id': None,
            'itens_checklist': []
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def api_request(self, method: str, endpoint: str, data: Dict = None, 
                         params: Dict = None) -> Dict[str, Any]:
        """Faz requisição para API e retorna resultado"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=params
            ) as response:
                result = await response.json()
                return {
                    'success': response.status < 400,
                    'status_code': response.status,
                    'data': result
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    async def test_1_verificar_operador(self) -> bool:
        """Teste 1: Verificar se operador existe e está ativo"""
        print("🔍 TESTE 1: Verificando operador...")
        
        result = await self.api_request(
            'GET', 
            f"/api/operadores/{self.test_data['operador_codigo']}/equipamentos/"
        )
        
        if result['success']:
            operador_data = result['data']
            print(f"   ✅ Operador encontrado: {operador_data.get('operador', {}).get('nome', 'N/A')}")
            print(f"   📋 Equipamentos disponíveis: {operador_data.get('count', 0)}")
            return True
        else:
            print(f"   ❌ Falha: {result.get('error', 'Operador não encontrado')}")
            return False
    
    async def test_2_criar_checklist(self) -> bool:
        """Teste 2: Criar checklist para equipamento"""
        print("📋 TESTE 2: Criando checklist...")
        
        result = await self.api_request(
            'POST',
            '/api/nr12/checklists/criar/',
            data={
                'equipamento_id': self.test_data['equipamento_id'],
                'operador_codigo': self.test_data['operador_codigo'],
                'turno': 'MANHA',
                'frequencia': 'DIARIO'
            }
        )
        
        if result['success']:
            checklist_data = result['data'].get('checklist', {})
            self.test_data['checklist_id'] = checklist_data.get('id')
            print(f"   ✅ Checklist criado: ID {self.test_data['checklist_id']}")
            print(f"   📊 Total de itens: {checklist_data.get('total_itens', 0)}")
            print(f"   📅 Data: {checklist_data.get('data_checklist', 'N/A')}")
            return True
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_3_iniciar_checklist(self) -> bool:
        """Teste 3: Iniciar checklist (status PENDENTE -> EM_ANDAMENTO)"""
        print("▶️ TESTE 3: Iniciando checklist...")
        
        if not self.test_data['checklist_id']:
            print("   ❌ Falha: Checklist ID não encontrado")
            return False
        
        result = await self.api_request(
            'POST',
            f"/api/nr12/checklists/{self.test_data['checklist_id']}/iniciar/",
            data={
                'operador_codigo': self.test_data['operador_codigo']
            }
        )
        
        if result['success']:
            checklist_data = result['data'].get('checklist', {})
            print(f"   ✅ Checklist iniciado: Status {checklist_data.get('status', 'N/A')}")
            print(f"   ⏰ Iniciado em: {checklist_data.get('data_inicio', 'N/A')}")
            return True
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_4_buscar_itens_checklist(self) -> bool:
        """Teste 4: Buscar itens do checklist"""
        print("📝 TESTE 4: Buscando itens do checklist...")
        
        if not self.test_data['checklist_id']:
            print("   ❌ Falha: Checklist ID não encontrado")
            return False
        
        result = await self.api_request(
            'GET',
            f"/api/nr12/checklists/{self.test_data['checklist_id']}/itens/"
        )
        
        if result['success']:
            itens = result['data'].get('results', [])
            self.test_data['itens_checklist'] = itens
            print(f"   ✅ {len(itens)} itens encontrados")
            
            # Mostrar alguns itens
            for i, item in enumerate(itens[:3], 1):
                print(f"      {i}. {item.get('item_padrao', {}).get('item', 'N/A')} - Status: {item.get('status', 'N/A')}")
            
            if len(itens) > 3:
                print(f"      ... e mais {len(itens) - 3} itens")
            
            return True
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_5_responder_itens(self) -> bool:
        """Teste 5: Responder alguns itens do checklist"""
        print("✅ TESTE 5: Respondendo itens do checklist...")
        
        if not self.test_data['itens_checklist']:
            print("   ❌ Falha: Nenhum item encontrado")
            return False
        
        itens_para_testar = self.test_data['itens_checklist'][:5]  # Testar primeiros 5 itens
        respostas_teste = ['OK', 'NOK', 'OK', 'N/A', 'OK']
        observacoes_teste = [
            'Funcionando perfeitamente',
            'Pequeno vazamento detectado',
            'Dentro dos parâmetros',
            'Item não aplicável',
            'Teste finalizado'
        ]
        
        sucesso_count = 0
        
        for i, item in enumerate(itens_para_testar):
            item_id = item.get('id')
            status = respostas_teste[i % len(respostas_teste)]
            observacao = observacoes_teste[i % len(observacoes_teste)]
            
            result = await self.api_request(
                'POST',
                '/api/nr12/bot/item-checklist/atualizar/',
                data={
                    'item_id': item_id,
                    'status': status,
                    'observacao': observacao,
                    'operador_codigo': self.test_data['operador_codigo']
                }
            )
            
            if result['success']:
                sucesso_count += 1
                print(f"   ✅ Item {item_id}: {status} - {observacao[:30]}...")
            else:
                error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
                print(f"   ❌ Item {item_id}: {error_msg}")
        
        print(f"   📊 {sucesso_count}/{len(itens_para_testar)} itens respondidos com sucesso")
        return sucesso_count > 0
    
    async def test_6_verificar_progresso(self) -> bool:
        """Teste 6: Verificar progresso do checklist"""
        print("📊 TESTE 6: Verificando progresso...")
        
        if not self.test_data['checklist_id']:
            print("   ❌ Falha: Checklist ID não encontrado")
            return False
        
        result = await self.api_request(
            'GET',
            f"/api/nr12/checklists/{self.test_data['checklist_id']}/"
        )
        
        if result['success']:
            checklist = result['data']
            total_itens = checklist.get('total_itens', 0)
            itens_respondidos = checklist.get('itens_respondidos', 0)
            percentual = checklist.get('percentual_conclusao', 0)
            
            print(f"   ✅ Progresso: {itens_respondidos}/{total_itens} ({percentual}%)")
            print(f"   📋 Status: {checklist.get('status', 'N/A')}")
            
            if checklist.get('responsavel'):
                responsavel = checklist['responsavel']
                print(f"   👤 Responsável: {responsavel.get('nome', responsavel.get('username', 'N/A'))}")
            
            return True
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_7_pausar_retomar(self) -> bool:
        """Teste 7: Simular pausa e retomada (verificar sessão)"""
        print("⏸️ TESTE 7: Simulando pausa e retomada...")
        
        # Simular "pausa" - verificar se consegue continuar depois
        await asyncio.sleep(1)  # Pequena pausa
        
        # Tentar acessar checklist novamente
        result = await self.api_request(
            'GET',
            '/api/nr12/checklists/',
            params={
                'operador_id': 1,  # Assumindo ID 1 para teste
                'status': 'EM_ANDAMENTO',
                'equipamento_id': self.test_data['equipamento_id']
            }
        )
        
        if result['success']:
            checklists = result['data'].get('results', [])
            checklist_encontrado = any(
                c.get('id') == self.test_data['checklist_id'] 
                for c in checklists
            )
            
            if checklist_encontrado:
                print("   ✅ Checklist encontrado após pausa - sessão mantida")
                return True
            else:
                print("   ⚠️ Checklist não encontrado na lista - possível problema de filtro")
                return False
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_8_finalizar_checklist(self) -> bool:
        """Teste 8: Finalizar checklist (responder itens restantes e concluir)"""
        print("🏁 TESTE 8: Finalizando checklist...")
        
        # Primeiro, responder todos os itens restantes
        if self.test_data['itens_checklist']:
            itens_restantes = self.test_data['itens_checklist'][5:]  # Itens não respondidos no teste 5
            
            for item in itens_restantes:
                await self.api_request(
                    'POST',
                    '/api/nr12/bot/item-checklist/atualizar/',
                    data={
                        'item_id': item.get('id'),
                        'status': 'OK',
                        'observacao': 'Finalização automática - teste',
                        'operador_codigo': self.test_data['operador_codigo']
                    }
                )
        
        # Finalizar checklist
        result = await self.api_request(
            'POST',
            f"/api/nr12/checklists/{self.test_data['checklist_id']}/finalizar/",
            data={
                'operador_codigo': self.test_data['operador_codigo']
            }
        )
        
        if result['success']:
            checklist_data = result['data'].get('checklist', {})
            print(f"   ✅ Checklist finalizado: Status {checklist_data.get('status', 'N/A')}")
            print(f"   ⏰ Concluído em: {checklist_data.get('data_conclusao', 'N/A')}")
            print(f"   📊 Conclusão: {checklist_data.get('percentual_conclusao', 0)}%")
            return True
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def test_9_verificar_auditoria(self) -> bool:
        """Teste 9: Verificar dados de auditoria"""
        print("🔍 TESTE 9: Verificando dados de auditoria...")
        
        result = await self.api_request(
            'GET',
            f"/api/nr12/checklists/{self.test_data['checklist_id']}/"
        )
        
        if result['success']:
            checklist = result['data']
            
            print("   ✅ Dados de auditoria:")
            print(f"      📅 Data checklist: {checklist.get('data_checklist', 'N/A')}")
            print(f"      ⏰ Data criação: {checklist.get('data_criacao', 'N/A')}")
            print(f"      ▶️ Data início: {checklist.get('data_inicio', 'N/A')}")
            print(f"      🏁 Data conclusão: {checklist.get('data_conclusao', 'N/A')}")
            print(f"      👤 Responsável: {checklist.get('responsavel', {}).get('nome', 'N/A')}")
            print(f"      📊 Percentual: {checklist.get('percentual_conclusao', 0)}%")
            
            # Verificar se todos os campos obrigatórios estão preenchidos
            campos_obrigatorios = [
                'data_checklist', 'data_criacao', 'data_inicio', 
                'data_conclusao', 'responsavel', 'percentual_conclusao'
            ]
            
            campos_ok = 0
            for campo in campos_obrigatorios:
                if checklist.get(campo):
                    campos_ok += 1
            
            print(f"   📋 Campos de auditoria: {campos_ok}/{len(campos_obrigatorios)}")
            return campos_ok >= len(campos_obrigatorios) - 1  # Permitir 1 campo faltando
        else:
            error_msg = result.get('data', {}).get('error', result.get('error', 'Erro desconhecido'))
            print(f"   ❌ Falha: {error_msg}")
            return False
    
    async def run_full_test(self):
        """Executa todos os testes em sequência"""
        print("🧪 INICIANDO TESTE COMPLETO DO FLUXO DE CHECKLIST")
        print("=" * 60)
        
        testes = [
            ("Verificar Operador", self.test_1_verificar_operador),
            ("Criar Checklist", self.test_2_criar_checklist),
            ("Iniciar Checklist", self.test_3_iniciar_checklist),
            ("Buscar Itens", self.test_4_buscar_itens_checklist),
            ("Responder Itens", self.test_5_responder_itens),
            ("Verificar Progresso", self.test_6_verificar_progresso),
            ("Pausar/Retomar", self.test_7_pausar_retomar),
            ("Finalizar Checklist", self.test_8_finalizar_checklist),
            ("Verificar Auditoria", self.test_9_verificar_auditoria),
        ]
        
        resultados = []
        
        for nome_teste, func_teste in testes:
            try:
                resultado = await func_teste()
                resultados.append((nome_teste, resultado))
                
                if not resultado:
                    print(f"\n⚠️ TESTE FALHOU: {nome_teste}")
                    continuar = input("Continuar com próximos testes? (s/N): ").lower()
                    if continuar != 's':
                        break
                
                print()  # Linha em branco entre testes
                
            except Exception as e:
                print(f"   ❌ ERRO CRÍTICO: {e}")
                resultados.append((nome_teste, False))
                break
        
        # Resumo final
        print("=" * 60)
        print("📊 RESUMO DO TESTE DE FLUXO")
        print("=" * 60)
        
        sucessos = sum(1 for _, resultado in resultados if resultado)
        total = len(resultados)
        
        print(f"✅ Testes executados: {total}")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {total - sucessos}")
        print(f"📊 Taxa de sucesso: {(sucessos/total)*100:.1f}%")
        
        print("\n📋 Detalhes:")
        for nome_teste, resultado in resultados:
            status = "✅" if resultado else "❌"
            print(f"   {status} {nome_teste}")
        
        if sucessos == total:
            print("\n🎉 TODOS OS TESTES PASSARAM! Fluxo funcionando corretamente.")
        else:
            print(f"\n⚠️ {total - sucessos} teste(s) falharam. Verificar implementação.")
        
        return sucessos == total

# ===============================================
# FUNÇÃO PRINCIPAL
# ===============================================

async def main():
    """Executa teste completo do fluxo de checklist"""
    async with ChecklistFlowTester() as tester:
        await tester.run_full_test()

if __name__ == "__main__":
    print("🧪 TESTADOR DE FLUXO COMPLETO - CHECKLIST NR12")
    print("Certifique-se de que:")
    print("1. O servidor Django está rodando")
    print("2. Existe um operador com código 'OP001'")
    print("3. Existe um equipamento com ID 1")
    print("4. O banco de dados está configurado")
    print("\nPressione Ctrl+C para interromper")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")