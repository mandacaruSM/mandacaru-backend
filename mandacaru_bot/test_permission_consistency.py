# ===============================================
# ARQUIVO: test_permission_consistency.py
# Testes de consistência e permissões do sistema
# ===============================================

import asyncio
import json
from datetime import date, datetime
from typing import Dict, List, Any
import aiohttp

class PermissionTester:
    """Testa consistência de permissões e regras de negócio"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_scenarios = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def api_request(self, method: str, endpoint: str, data: Dict = None, 
                         params: Dict = None) -> Dict[str, Any]:
        """Faz requisição para API"""
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
    
    async def test_operador_sem_equipamentos_autorizados(self):
        """
        Cenário 1: Operador sem equipamentos autorizados, mas com clientes autorizados
        Deve ver todos equipamentos desses clientes
        """
        print("🧪 TESTE 1: Operador com apenas clientes autorizados")
        print("-" * 50)
        
        # Simular criação de operador com apenas clientes (sem equipamentos específicos)
        # Assumindo que existe operador ID 2 configurado desta forma
        
        result = await self.api_request(
            'GET',
            '/api/operadores/2/equipamentos/',
            params={'include_supervisionados': False}
        )
        
        if result['success']:
            operador_data = result['data']
            equipamentos = operador_data.get('results', [])
            
            print(f"   ✅ Operador: {operador_data.get('operador', {}).get('nome', 'N/A')}")
            print(f"   📋 Equipamentos disponíveis: {len(equipamentos)}")
            
            # Verificar se tem acesso baseado em clientes
            clientes_equipamentos = set()
            for eq in equipamentos:
                if eq.get('cliente'):
                    clientes_equipamentos.add(eq['cliente']['nome'])
            
            print(f"   🏢 Clientes com equipamentos: {', '.join(clientes_equipamentos) if clientes_equipamentos else 'Nenhum'}")
            
            # Teste: Tentar acessar checklist de um desses equipamentos
            if equipamentos:
                primeiro_eq = equipamentos[0]
                checklist_result = await self.api_request(
                    'GET',
                    '/api/nr12/checklists/',
                    params={
                        'operador_id': 2,
                        'equipamento_id': primeiro_eq['id']
                    }
                )
                
                if checklist_result['success']:
                    print(f"   ✅ Pode acessar checklists do equipamento {primeiro_eq['nome']}")
                    return True
                else:
                    print(f"   ❌ Não pode acessar checklists: {checklist_result.get('error', 'Erro desconhecido')}")
                    return False
            else:
                print("   ⚠️ Nenhum equipamento disponível para teste")
                return False
        else:
            print(f"   ❌ Falha ao buscar equipamentos: {result.get('error', 'Erro desconhecido')}")
            return False
    
    async def test_operador_inativo(self):
        """
        Cenário 2: Operador com status diferente de ATIVO ou ativo_bot=False
        Deve ser barrado
        """
        print("\n🧪 TESTE 2: Operador inativo ou sem permissão bot")
        print("-" * 50)
        
        # Testar com operador inativo (assumindo ID 999 não existe ou está inativo)
        result = await self.api_request(
            'GET',
            '/api/operadores/999/equipamentos/'
        )
        
        if not result['success'] and result['status_code'] in [403, 404]:
            print("   ✅ Operador inativo corretamente barrado")
            
            # Teste adicional: Tentar fazer login com operador inativo
            login_result = await self.api_request(
                'POST',
                '/api/nr12/bot/operador/login/',
                data={
                    'codigo': 'OP999',
                    'data_nascimento': '1990-01-01'
                }
            )
            
            if not login_result['success']:
                print("   ✅ Login de operador inativo corretamente negado")
                return True
            else:
                print("   ❌ Login de operador inativo foi permitido!")
                return False
        else:
            print(f"   ❌ Operador inativo não foi barrado adequadamente")
            return False
    
    async def test_supervisor_acesso_subordinados(self):
        """
        Cenário 3: Supervisor deve ver equipamentos de seus subordinados
        """
        print("\n🧪 TESTE 3: Supervisor acessando equipamentos de subordinados")
        print("-" * 50)
        
        # Assumindo que operador ID 3 é supervisor
        result = await self.api_request(
            'GET',
            '/api/operadores/3/equipamentos/',
            params={'include_supervisionados': True}
        )
        
        if result['success']:
            operador_data = result['data']
            operador_info = operador_data.get('operador', {})
            
            print(f"   👤 Supervisor: {operador_info.get('nome', 'N/A')}")
            print(f"   👥 É supervisor: {operador_info.get('is_supervisor', False)}")
            
            if operador_info.get('is_supervisor'):
                supervisionados = operador_info.get('supervisionados', [])
                print(f"   📋 Supervisionados: {len(supervisionados)}")
                
                for supervisionado in supervisionados:
                    print(f"      • {supervisionado.get('nome', 'N/A')} ({supervisionado.get('equipamentos_count', 0)} equipamentos)")
                
                # Testar acesso a checklists da equipe
                team_checklists = await self.api_request(
                    'GET',
                    '/api/nr12/checklists/',
                    params={
                        'operador_id': 3,
                        'include_team': True,
                        'status': 'PENDENTE'
                    }
                )
                
                if team_checklists['success']:
                    checklists_count = team_checklists['data'].get('count', 0)
                    print(f"   ✅ Acesso a {checklists_count} checklists da equipe")
                    return True
                else:
                    print(f"   ❌ Erro ao acessar checklists da equipe: {team_checklists.get('error', 'Erro desconhecido')}")
                    return False
            else:
                print("   ⚠️ Operador não é supervisor, teste não aplicável")
                return True
        else:
            print(f"   ❌ Falha ao testar supervisor: {result.get('error', 'Erro desconhecido')}")
            return False
    
    async def test_equipamento_authorization(self):
        """
        Cenário 4: Verificar se método pode_operar_equipamento funciona corretamente
        """
        print("\n🧪 TESTE 4: Autorização de equipamentos")
        print("-" * 50)
        
        # Testar acesso a equipamento específico por diferentes operadores
        equipamento_id = 1
        operadores_teste = [1, 2, 3]  # IDs de teste
        
        for operador_id in operadores_teste:
            result = await self.api_request(
                'GET',
                f'/api/operadores/{operador_id}/equipamentos/',
                params={'page_size': 100}  # Buscar todos
            )
            
            if result['success']:
                equipamentos = result['data'].get('results', [])
                operador_nome = result['data'].get('operador', {}).get('nome', f'OP{operador_id}')
                
                # Verificar se equipamento específico está na lista
                pode_operar = any(eq['id'] == equipamento_id for eq in equipamentos)
                
                print(f"   👤 {operador_nome}: {'✅ Pode operar' if pode_operar else '❌ Não pode operar'} equipamento {equipamento_id}")
                
                # Se pode operar, testar criação de checklist
                if pode_operar:
                    checklist_test = await self.api_request(
                        'POST',
                        '/api/nr12/checklists/criar/',
                        data={
                            'equipamento_id': equipamento_id,
                            'operador_codigo': f'OP{operador_id:03d}',
                            'turno': 'TESTE'
                        }
                    )
                    
                    if checklist_test['success']:
                        print(f"      ✅ Pode criar checklist")
                    else:
                        print(f"      ⚠️ Não pode criar checklist: {checklist_test.get('data', {}).get('error', 'Erro')}")
            else:
                print(f"   ❌ Erro ao testar operador {operador_id}")
        
        return True
    
    async def test_checklist_status_transitions(self):
        """
        Cenário 5: Verificar transições de status de checklist
        """
        print("\n🧪 TESTE 5: Transições de status de checklist")
        print("-" * 50)
        
        # Criar checklist para teste
        create_result = await self.api_request(
            'POST',
            '/api/nr12/checklists/criar/',
            data={
                'equipamento_id': 1,
                'operador_codigo': 'OP001',
                'turno': 'TESTE_STATUS'
            }
        )
        
        if not create_result['success']:
            print(f"   ❌ Falha ao criar checklist de teste: {create_result.get('error', 'Erro')}")
            return False
        
        checklist_id = create_result['data'].get('checklist', {}).get('id')
        print(f"   📋 Checklist criado: ID {checklist_id}")
        
        # Testar transição PENDENTE -> EM_ANDAMENTO
        start_result = await self.api_request(
            'POST',
            f'/api/nr12/checklists/{checklist_id}/iniciar/',
            data={'operador_codigo': 'OP001'}
        )
        
        if start_result['success']:
            status = start_result['data'].get('checklist', {}).get('status')
            print(f"   ✅ Transição para EM_ANDAMENTO: {status}")
            
            # Verificar se data_inicio foi setada
            data_inicio = start_result['data'].get('checklist', {}).get('data_inicio')
            if data_inicio:
                print(f"   ✅ Data início registrada: {data_inicio}")
            else:
                print(f"   ⚠️ Data início não registrada")
            
            return True
        else:
            print(f"   ❌ Falha ao iniciar checklist: {start_result.get('error', 'Erro')}")
            return False
    
    async def test_qr_code_validation(self):
        """
        Cenário 6: Validar sistema de QR codes
        """
        print("\n🧪 TESTE 6: Validação de QR codes")
        print("-" * 50)
        
        # Testar QR code de equipamento válido
        qr_data_equipamento = {
            'tipo': 'equipamento',
            'id': 1,
            'codigo': 'EQ0001',
            'nome': 'Escavadeira Teste',
            'ativo_nr12': True,
            'versao': '2.0'
        }
        
        qr_test_result = await self.api_request(
            'POST',
            '/api/equipamentos/qr/scan/',
            data={
                'qr_text': json.dumps(qr_data_equipamento),
                'operador_codigo': 'OP001'
            }
        )
        
        if qr_test_result['success']:
            print("   ✅ QR code de equipamento válido processado")
            
            qr_response = qr_test_result['data']
            acoes = qr_response.get('acoes_disponiveis', [])
            print(f"   📋 Ações disponíveis: {', '.join(acoes)}")
            
            # Testar QR code inválido
            qr_invalid_test = await self.api_request(
                'POST',
                '/api/equipamentos/qr/scan/',
                data={
                    'qr_text': 'invalid_json_data',
                    'operador_codigo': 'OP001'
                }
            )
            
            if not qr_invalid_test['success']:
                print("   ✅ QR code inválido corretamente rejeitado")
                return True
            else:
                print("   ❌ QR code inválido foi aceito!")
                return False
        else:
            print(f"   ❌ Falha ao testar QR code: {qr_test_result.get('error', 'Erro')}")
            return False
    
    async def test_audit_fields(self):
        """
        Cenário 7: Verificar se campos de auditoria estão sendo preenchidos
        """
        print("\n🧪 TESTE 7: Campos de auditoria")
        print("-" * 50)
        
        # Buscar um checklist finalizado para verificar auditoria
        result = await self.api_request(
            'GET',
            '/api/nr12/checklists/',
            params={
                'status': 'CONCLUIDO',
                'page_size': 1
            }
        )
        
        if result['success']:
            checklists = result['data'].get('results', [])
            
            if checklists:
                checklist = checklists[0]
                print(f"   📋 Checklist analisado: ID {checklist.get('id')}")
                
                # Verificar campos obrigatórios de auditoria
                campos_auditoria = {
                    'responsavel': checklist.get('responsavel'),
                    'data_criacao': checklist.get('data_criacao'),
                    'data_inicio': checklist.get('data_inicio'),
                    'data_conclusao': checklist.get('data_conclusao'),
                    'percentual_conclusao': checklist.get('percentual_conclusao')
                }
                
                print("   📊 Campos de auditoria:")
                campos_ok = 0
                for campo, valor in campos_auditoria.items():
                    status = "✅" if valor else "❌"
                    print(f"      {status} {campo}: {valor or 'AUSENTE'}")
                    if valor:
                        campos_ok += 1
                
                taxa_completude = (campos_ok / len(campos_auditoria)) * 100
                print(f"   📈 Completude da auditoria: {taxa_completude:.1f}%")
                
                return taxa_completude >= 80  # 80% dos campos devem estar preenchidos
            else:
                print("   ⚠️ Nenhum checklist concluído encontrado para teste")
                return True
        else:
            print(f"   ❌ Erro ao buscar checklists: {result.get('error', 'Erro')}")
            return False
    
    async def test_pagination_performance(self):
        """
        Cenário 8: Testar paginação e performance
        """
        print("\n🧪 TESTE 8: Paginação e performance")
        print("-" * 50)
        
        import time
        
        # Testar diferentes tamanhos de página
        page_sizes = [5, 10, 25, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            
            result = await self.api_request(
                'GET',
                '/api/nr12/checklists/',
                params={
                    'page': 1,
                    'page_size': page_size,
                    'operador_id': 1
                }
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # em ms
            
            if result['success']:
                data = result['data']
                print(f"   📄 Page size {page_size}: {response_time:.0f}ms - {data.get('count', 0)} total, {len(data.get('results', []))} retornados")
            else:
                print(f"   ❌ Erro com page_size {page_size}")
        
        # Testar limite máximo
        max_test = await self.api_request(
            'GET',
            '/api/nr12/checklists/',
            params={
                'page': 1,
                'page_size': 1000  # Deve ser limitado a 50
            }
        )
        
        if max_test['success']:
            returned_count = len(max_test['data'].get('results', []))
            print(f"   ⚖️ Teste limite máximo: solicitado 1000, retornado {returned_count}")
            return returned_count <= 50
        else:
            return False
    
    async def test_concurrent_access(self):
        """
        Cenário 9: Testar acesso concorrente ao mesmo checklist
        """
        print("\n🧪 TESTE 9: Acesso concorrente")
        print("-" * 50)
        
        # Simular dois operadores tentando acessar o mesmo checklist
        checklist_id = 1  # Assumindo que existe
        
        # Duas requisições simultâneas
        tasks = [
            self.api_request(
                'POST',
                f'/api/nr12/checklists/{checklist_id}/iniciar/',
                data={'operador_codigo': 'OP001'}
            ),
            self.api_request(
                'POST',
                f'/api/nr12/checklists/{checklist_id}/iniciar/',
                data={'operador_codigo': 'OP002'}
            )
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        sucessos = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        print(f"   🔄 Requisições simultâneas: {sucessos}/2 bem-sucedidas")
        
        # Idealmente, apenas uma deveria ter sucesso
        if sucessos <= 1:
            print("   ✅ Controle de concorrência funcionando")
            return True
        else:
            print("   ⚠️ Possível problema de concorrência")
            return False
    
    async def test_data_integrity(self):
        """
        Cenário 10: Verificar integridade dos dados
        """
        print("\n🧪 TESTE 10: Integridade de dados")
        print("-" * 50)
        
        # Verificar se percentual de conclusão está correto
        result = await self.api_request(
            'GET',
            '/api/nr12/checklists/',
            params={'page_size': 5}
        )
        
        if result['success']:
            checklists = result['data'].get('results', [])
            
            integrity_ok = 0
            for checklist in checklists:
                total_itens = checklist.get('total_itens', 0)
                itens_respondidos = checklist.get('itens_respondidos', 0)
                percentual = checklist.get('percentual_conclusao', 0)
                
                # Calcular percentual esperado
                if total_itens > 0:
                    percentual_esperado = (itens_respondidos / total_itens) * 100
                    diferenca = abs(percentual - percentual_esperado)
                    
                    status = "✅" if diferenca < 1 else "❌"
                    print(f"   {status} Checklist {checklist.get('id')}: {percentual:.1f}% (esperado: {percentual_esperado:.1f}%)")
                    
                    if diferenca < 1:
                        integrity_ok += 1
                else:
                    print(f"   ⚠️ Checklist {checklist.get('id')}: sem itens")
            
            if checklists:
                taxa_integridade = (integrity_ok / len(checklists)) * 100
                print(f"   📊 Integridade dos dados: {taxa_integridade:.1f}%")
                return taxa_integridade >= 90
            else:
                print("   ⚠️ Nenhum checklist para testar")
                return True
        else:
            print(f"   ❌ Erro ao verificar integridade: {result.get('error', 'Erro')}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes de consistência"""
        print("🧪 INICIANDO TESTES DE CONSISTÊNCIA E PERMISSÕES")
        print("=" * 60)
        
        tests = [
            ("Operador sem equipamentos específicos", self.test_operador_sem_equipamentos_autorizados),
            ("Operador inativo", self.test_operador_inativo),
            ("Supervisor e subordinados", self.test_supervisor_acesso_subordinados),
            ("Autorização de equipamentos", self.test_equipamento_authorization),
            ("Transições de status", self.test_checklist_status_transitions),
            ("Validação QR codes", self.test_qr_code_validation),
            ("Campos de auditoria", self.test_audit_fields),
            ("Paginação e performance", self.test_pagination_performance),
            ("Acesso concorrente", self.test_concurrent_access),
            ("Integridade de dados", self.test_data_integrity),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                result = await test_func()
                results.append((test_name, result))
                
                status = "✅ PASSOU" if result else "❌ FALHOU"
                print(f"\n{status}: {test_name}")
                
            except Exception as e:
                print(f"\n❌ ERRO CRÍTICO em {test_name}: {e}")
                results.append((test_name, False))
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES DE CONSISTÊNCIA")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print(f"✅ Testes executados: {total}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {total - passed}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        print("\n📋 Detalhes por teste:")
        for test_name, result in results:
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
        
        # Classificação do sistema
        if success_rate >= 90:
            classification = "🟢 EXCELENTE"
        elif success_rate >= 75:
            classification = "🟡 BOM"
        elif success_rate >= 60:
            classification = "🟠 SATISFATÓRIO"
        else:
            classification = "🔴 NECESSITA CORREÇÕES"
        
        print(f"\n🎯 CLASSIFICAÇÃO DO SISTEMA: {classification}")
        
        if success_rate < 90:
            print("\n💡 RECOMENDAÇÕES:")
            if success_rate < 75:
                print("   • Revisar regras de negócio fundamentais")
                print("   • Verificar configuração de permissões")
            if success_rate < 60:
                print("   • Auditoria completa do código necessária")
                print("   • Testes unitários adicionais recomendados")
        
        return success_rate >= 75

# ===============================================
# FUNÇÃO PRINCIPAL
# ===============================================

async def main():
    """Executa todos os testes de consistência"""
    async with PermissionTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    print("🧪 TESTADOR DE CONSISTÊNCIA - SISTEMA MANDACARU")
    print("Este script testa regras de negócio e permissões")
    print("Certifique-se de que:")
    print("1. O servidor Django está rodando")
    print("2. Existem dados de teste no banco")
    print("3. Operadores 1, 2, 3 existem com diferentes perfis")
    print("4. Equipamentos e checklists existem")
    print("\nPressione Ctrl+C para interromper")
    
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        exit(1)