# ================================================================
# SCRIPT PARA VERIFICAR EQUIPAMENTOS - Execute no Django Shell
# python manage.py shell
# ================================================================

from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento

print("🔍 VERIFICANDO EQUIPAMENTOS NO SISTEMA")
print("=" * 60)

# 1. Verificar categorias
categorias = CategoriaEquipamento.objects.all()
print(f"📂 CATEGORIAS: {categorias.count()}")
for cat in categorias:
    print(f"   - {cat.codigo}: {cat.nome} (Prefixo: {cat.prefixo_codigo})")

print()

# 2. Verificar equipamentos
equipamentos = Equipamento.objects.all().select_related('categoria', 'cliente')
print(f"🔧 EQUIPAMENTOS: {equipamentos.count()}")

if equipamentos.count() == 0:
    print("❌ NENHUM EQUIPAMENTO ENCONTRADO!")
    print("\n💡 CRIANDO EQUIPAMENTOS DE TESTE...")
    
    # Criar categoria de teste se não existir
    categoria, created = CategoriaEquipamento.objects.get_or_create(
        codigo='EQ',
        defaults={
            'nome': 'Equipamentos Gerais',
            'prefixo_codigo': 'EQ',
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Categoria criada: {categoria.nome}")
    
    # Criar cliente de teste se não existir
    from backend.apps.clientes.models import Cliente
    cliente, created = Cliente.objects.get_or_create(
        cnpj='00000000000000',
        defaults={
            'razao_social': 'Cliente Teste',
            'nome_fantasia': 'Teste',
            'telefone': '11999999999',
            'email': 'teste@teste.com'
        }
    )
    
    if created:
        print(f"✅ Cliente criado: {cliente.razao_social}")
    
    # Criar empreendimento de teste se não existir
    from backend.apps.empreendimentos.models import Empreendimento
    empreendimento, created = Empreendimento.objects.get_or_create(
        nome='Empreendimento Teste',
        defaults={
            'descricao': 'Empreendimento para testes',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Empreendimento criado: {empreendimento.nome}")
    
    # Criar tipo NR12 de teste
    from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
    tipo_nr12, created = TipoEquipamentoNR12.objects.get_or_create(
        nome='Equipamento Geral',
        defaults={
            'descricao': 'Tipo geral para equipamentos',
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Tipo NR12 criado: {tipo_nr12.nome}")
    
    # Criar equipamentos de teste
    equipamentos_teste = [
        {
            'nome': 'Escavadeira CAT 320D',
            'marca': 'Caterpillar',
            'modelo': '320D'
        },
        {
            'nome': 'Retroescavadeira JCB 3CX',
            'marca': 'JCB', 
            'modelo': '3CX'
        },
        {
            'nome': 'Pá Carregadeira CAT 950H',
            'marca': 'Caterpillar',
            'modelo': '950H'
        }
    ]
    
    for eq_data in equipamentos_teste:
        eq = Equipamento.objects.create(
            nome=eq_data['nome'],
            marca=eq_data['marca'],
            modelo=eq_data['modelo'],
            categoria=categoria,
            cliente=cliente,
            empreendimento=empreendimento,
            ativo=True,
            ativo_nr12=True,
            status='OPERACIONAL',
            status_operacional='DISPONIVEL',
            tipo_nr12=tipo_nr12,
            frequencias_checklist=['DIARIA']
        )
        print(f"✅ Equipamento criado: {eq.nome} (Código: {eq.codigo})")
    
    # Recarregar equipamentos
    equipamentos = Equipamento.objects.all().select_related('categoria', 'cliente')

print(f"\n📋 LISTA DE EQUIPAMENTOS:")
print("-" * 40)

for i, eq in enumerate(equipamentos, 1):
    print(f"{i}. {eq.nome}")
    print(f"   ID: {eq.id}")
    print(f"   Código: {eq.codigo}")
    print(f"   Categoria: {eq.categoria.nome if eq.categoria else 'N/A'}")
    print(f"   Status: {eq.status}")
    print(f"   Ativo: {eq.ativo}")
    print(f"   Ativo NR12: {eq.ativo_nr12}")
    print(f"   Tipo NR12: {eq.tipo_nr12.nome if eq.tipo_nr12 else '❌ NÃO CONFIGURADO'}")
    print()

# 3. Teste de códigos específicos
print("🧪 TESTE DE CÓDIGOS:")
print("-" * 40)

codigos_teste = ['EQ0001', 'EQ0002', 'EQ0003', '1', '2', '3']

for codigo in codigos_teste:
    encontrado = False
    
    if codigo.isdigit():
        # Buscar por ID
        eq = Equipamento.objects.filter(id=int(codigo)).first()
        if eq:
            print(f"✅ ID {codigo}: {eq.nome} (Código: {eq.codigo})")
            encontrado = True
    else:
        # Buscar por código gerado
        for eq in equipamentos:
            if eq.codigo == codigo:
                print(f"✅ {codigo}: {eq.nome}")
                encontrado = True
                break
    
    if not encontrado:
        print(f"❌ {codigo}: Não encontrado")

print("\n" + "=" * 60)
print("✅ VERIFICAÇÃO CONCLUÍDA!")
print("\n💡 PRÓXIMOS PASSOS:")
print("1. Se equipamentos foram criados, teste o bot novamente")
print("2. Digite: OP0001 (login) e depois EQ0001 (equipamento)")
print("3. Se ainda não funcionar, verifique os handlers do bot")