from django.core.management.base import BaseCommand
from django.db import transaction
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
from backend.apps.clientes.models import Cliente
from backend.apps.empreendimentos.models import Empreendimento
from datetime import date


class Command(BaseCommand):
    help = 'Configura vínculos iniciais entre operadores, equipamentos e clientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Criar dados de teste para demonstração'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Configurando vínculos do sistema...'))

        if options['create_test_data']:
            self.criar_dados_teste()

        self.configurar_vinculos()
        self.verificar_configuracao()

    @transaction.atomic
    def criar_dados_teste(self):
        self.stdout.write('📝 Criando dados de teste...')

        cliente, _ = Cliente.objects.get_or_create(
            cnpj='12.345.678/0001-90',
            defaults={
                'razao_social': 'Construtora Mandacaru LTDA',
                'nome_fantasia': 'Mandacaru',
                'telefone': '(11) 99999-9999',
                'email': 'contato@mandacaru.com.br',
                'endereco': 'Rua das Obras, 123',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01000-000'
            }
        )

        empreendimento, _ = Empreendimento.objects.get_or_create(
            nome='Obra Central - SP',
            defaults={
                'cliente': cliente,
                'distancia_km': 25,
                'endereco': 'Rua da Obra, 456',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'data_inicio': date.today(),
                'ativo': True
            }
        )
        self.stdout.write(f'✅ Empreendimento criado: {empreendimento.nome}')

        categoria_padrao, _ = CategoriaEquipamento.objects.get_or_create(
            codigo='ESC',
            defaults={
                'nome': 'Escavadeiras',
                'descricao': 'Categoria de escavadeiras',
                'prefixo_codigo': 'ESC',
                'ativo': True
            }
        )

        equipamentos_dados = [
            {
                'nome': 'Escavadeira CAT 320D',
                'marca': 'Caterpillar',
                'modelo': '320D',
                'n_serie': 'CAT001'
            },
            {
                'nome': 'Retroescavadeira JCB 3CX',
                'marca': 'JCB',
                'modelo': '3CX',
                'n_serie': 'JCB002'
            },
            {
                'nome': 'Pá Carregadeira CAT 950H',
                'marca': 'Caterpillar',
                'modelo': '950H',
                'n_serie': 'CAT003'
            }
        ]

        equipamentos_criados = []
        for eq in equipamentos_dados:
            equipamento, _ = Equipamento.objects.get_or_create(
                n_serie=eq['n_serie'],
                defaults={
                    'nome': eq['nome'],
                    'descricao': '',
                    'marca': eq['marca'],
                    'modelo': eq['modelo'],
                    'categoria': categoria_padrao,
                    'cliente': cliente,
                    'empreendimento': empreendimento,
                    'ativo': True,
                    'ativo_nr12': True,
                    'status': 'OPERACIONAL',
                    'status_operacional': 'DISPONIVEL',
                    'frequencia_checklist': 'DIARIO'
                }
            )
            self.stdout.write(f'✅ Equipamento criado: {equipamento.nome}')
            equipamentos_criados.append(equipamento)

        operadores_dados = [
            {
                'nome': 'João Silva',
                'cpf': '123.456.789-01',
                'funcao': 'Operador de Escavadeira',
                'setor': 'Operações',
                'telefone': '(11) 91111-1111',
                'cnh_categoria': 'D'
            },
            {
                'nome': 'Maria Santos',
                'cpf': '123.456.789-02',
                'funcao': 'Operadora de Retroescavadeira',
                'setor': 'Operações',
                'telefone': '(11) 92222-2222',
                'cnh_categoria': 'C'
            },
            {
                'nome': 'Pedro Oliveira',
                'cpf': '123.456.789-03',
                'funcao': 'Supervisor de Operações',
                'setor': 'Supervisão',
                'telefone': '(11) 93333-3333',
                'cnh_categoria': 'D'
            }
        ]

        operadores_criados = []
        for idx, op in enumerate(operadores_dados):  # ← AQUI usamos idx corretamente
            operador, _ = Operador.objects.get_or_create(
                cpf=op['cpf'],
                defaults={
                    **op,
                    'data_nascimento': date(1985, 1, 1),
                    'endereco': 'Rua do Operador, 123',
                    'cidade': 'São Paulo',
                    'estado': 'SP',
                    'cep': '02000-000',
                    'data_admissao': date.today(),
                    'numero_documento': op['cpf'].replace('.', '').replace('-', ''),
                    'status': 'ATIVO',
                    'ativo_bot': True,
                    'chat_id_telegram': 100000 + idx,
                    'pode_fazer_checklist': True,
                    'pode_registrar_abastecimento': True,
                    'pode_reportar_anomalia': True,
                    'pode_ver_relatorios': 'Supervisor' in op['funcao']
                }
            )
            self.stdout.write(f'✅ Operador criado: {operador.nome}')
            operadores_criados.append(operador)

        self.stdout.write('🔗 Estabelecendo vínculos...')

        supervisor = next((op for op in operadores_criados if 'Supervisor' in op.funcao), None)
        if supervisor:
            supervisor.clientes_autorizados.set([cliente])
            supervisor.equipamentos_autorizados.set(equipamentos_criados)
            supervisor.empreendimentos_autorizados.set([empreendimento])
            self.stdout.write(f'✅ Supervisor {supervisor.nome}: acesso total')

        operador_escavadeira = next((op for op in operadores_criados if 'Escavadeira' in op.funcao), None)
        if operador_escavadeira:
            eq = next((e for e in equipamentos_criados if 'Escavadeira' in e.nome), None)
            operador_escavadeira.equipamentos_autorizados.set([eq])
            operador_escavadeira.clientes_autorizados.set([cliente])
            operador_escavadeira.empreendimentos_autorizados.set([empreendimento])
            self.stdout.write(f'✅ {operador_escavadeira.nome}: acesso à escavadeira')

        operador_retro = next((op for op in operadores_criados if 'Retroescavadeira' in op.funcao), None)
        if operador_retro:
            eq = next((e for e in equipamentos_criados if 'Retroescavadeira' in e.nome), None)
            operador_retro.equipamentos_autorizados.set([eq])
            operador_retro.clientes_autorizados.set([cliente])
            operador_retro.empreendimentos_autorizados.set([empreendimento])
            self.stdout.write(f'✅ {operador_retro.nome}: acesso à retroescavadeira')

    def configurar_vinculos(self):
        self.stdout.write('🔄 Configurando vínculos automáticos...')
        operadores = Operador.objects.filter(
            status='ATIVO',
            equipamentos_autorizados__isnull=True,
            clientes_autorizados__isnull=True
        ).distinct()
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        clientes = Cliente.objects.all()

        for op in operadores:
            op.equipamentos_autorizados.set(equipamentos)
            op.clientes_autorizados.set(clientes)
            self.stdout.write(f'✅ {op.nome}: acesso geral atribuído')

    def verificar_configuracao(self):
        self.stdout.write('🔍 Verificando configuração...')

        total_op = Operador.objects.filter(status='ATIVO').count()
        total_eq = Equipamento.objects.filter(ativo_nr12=True).count()
        total_cli = Cliente.objects.count()

        self.stdout.write(f'👥 Operadores ativos: {total_op}')
        self.stdout.write(f'🔧 Equipamentos NR12: {total_eq}')
        self.stdout.write(f'🏢 Clientes cadastrados: {total_cli}')
        self.stdout.write(self.style.SUCCESS('✅ Configuração de vínculos concluída!'))
