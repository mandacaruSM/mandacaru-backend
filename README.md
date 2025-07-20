# 🏗️ Mandacaru ERP Backend

Sistema de gestão empresarial completo com foco em equipamentos pesados, checklists NR12, e automação via bot Telegram.

## 📋 Funcionalidades Principais

### 🔧 Gestão de Equipamentos
- Cadastro completo de equipamentos pesados
- Categorização por tipo e função
- Controle de horímetro e manutenções
- Status operacional em tempo real

### 📋 Checklists NR12
- Checklists personalizados por tipo de equipamento
- QR Codes para acesso rápido via mobile
- Integração com bot Telegram
- Alertas automáticos de manutenção

### 🚨 Sistema de Alertas
- Manutenções preventivas vencidas
- Checklists pendentes
- Estoque baixo
- Contas a vencer

### 💰 Módulo Financeiro
- Contas a pagar e receber
- Controle de orçamentos
- Relatórios financeiros
- Integração com ordens de serviço

### 📊 Dashboard Executivo
- KPIs em tempo real
- Gráficos e estatísticas
- Histórico de performance
- Alertas críticos

### 🤖 Bot Telegram
- Acesso via QR Code
- Preenchimento de checklists
- Notificações automáticas
- Relatórios por mensagem

## 🚀 Tecnologias Utilizadas

- **Backend**: Django 5.2.4 + Django REST Framework
- **Banco de Dados**: PostgreSQL / SQLite
- **Cache**: Redis
- **Tasks Assíncronas**: Celery + Redis
- **QR Codes**: qrcode + Pillow
- **Containerização**: Docker + Docker Compose
- **Proxy**: Nginx

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/mandacaru-erp-backend.git
cd mandacaru-erp-backend
```

### 2. Configure o ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as variáveis necessárias
nano .env
```

### 3. Execute com Docker
```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Ou apenas os serviços essenciais
docker-compose up web db redis
```

### 4. Configuração inicial
```bash
# Execute as migrações
docker-compose exec web python manage.py migrate

# Crie um superusuário
docker-compose exec web python manage.py createsuperuser

# Configure dados iniciais
docker-compose exec web python manage.py sistema_mandacaru inicializar
```

## 🛠️ Instalação Manual (sem Docker)

### 1. Ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Dependências
```bash
pip install -r requirements.txt
```

### 3. Banco de dados
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Dados iniciais
```bash
# Configurar sistema
python manage.py sistema_mandacaru inicializar

# Criar categorias de equipamentos
python manage.py criar_categorias

# Configurar tipos NR12
python manage.py configurar_nr12
```

### 5. Executar servidor
```bash
python manage.py runserver
```

## 📱 Configuração do Bot Telegram

### 1. Criar bot no Telegram
1. Converse com @BotFather no Telegram
2. Execute `/newbot` e siga as instruções
3. Obtenha o token do bot

### 2. Configurar webhook
```bash
# Adicione o token no .env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/webhook/telegram/

# Configure o webhook
python manage.py configurar_telegram_webhook
```

## 🔧 Comandos de Gerenciamento

### Sistema
```bash
# Status completo do sistema
python manage.py sistema_mandacaru status

# Fazer backup
python manage.py sistema_mandacaru backup

# Limpeza de dados antigos
python manage.py sistema_mandacaru limpeza --dias 30

# Diagnóstico completo
python manage.py sistema_mandacaru diagnostico
```

### Checklists NR12
```bash
# Gerar checklists diários
python manage.py gerar_checklists_diarios

# Configurar tipos NR12
python manage.py configurar_nr12

# Criar checklist customizado
python manage.py criar_checklist
```

### QR Codes
```bash
# Gerar QR codes para checklists
python manage.py gerar_qr_codes --salvar-arquivos

# Gerar QR codes para equipamentos
python manage.py gerar_qr_equipamentos --todos

# Gerenciar QR codes
python manage.py qr_codes gerar --todos
```

### Relatórios
```bash
# Relatório geral NR12
python manage.py relatorio_nr12 --tipo resumo

# Relatório por equipamentos
python manage.py relatorio_nr12 --tipo equipamentos

# Relatório de performance
python manage.py relatorio_nr12 --tipo performance
```

## 📊 API Endpoints

### Autenticação
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/perfil/` - Perfil do usuário

### Dashboard
- `GET /api/dashboard/` - Dashboard principal
- `GET /api/dashboard/kpis/` - KPIs em tempo real
- `POST /api/dashboard/recalcular-kpis/` - Recalcular KPIs

### Equipamentos
- `GET /api/equipamentos/` - Listar equipamentos
- `POST /api/equipamentos/` - Criar equipamento
- `GET /api/equipamentos/{id}/` - Detalhes do equipamento

### Checklists NR12
- `GET /api/nr12/checklists/` - Listar checklists
- `POST /api/nr12/checklists/{id}/iniciar/` - Iniciar checklist
- `POST /api/nr12/checklists/{id}/finalizar/` - Finalizar checklist
- `GET /api/nr12/checklists/{id}/qr-code/` - QR Code do checklist

### Portal do Cliente
- `GET /api/portal/dashboard/resumo/` - Resumo para cliente
- `GET /api/portal/equipamentos/` - Equipamentos do cliente

### Acesso Público (QR Codes)
- `GET /qr/{uuid}/` - Acesso via QR Code do checklist
- `GET /equipamento/{id}/` - Acesso via QR Code do equipamento

## 🏗️ Estrutura do Projeto

```
backend/
├── apps/
│   ├── almoxarifado/          # Gestão de estoque
│   ├── auth_cliente/          # Autenticação personalizada
│   ├── bot_telegram/          # Integração Telegram
│   ├── cliente_portal/        # Portal do cliente
│   ├── clientes/              # Cadastro de clientes
│   ├── core/                  # Funcionalidades core
│   ├── dashboard/             # Dashboard e KPIs
│   ├── empreendimentos/       # Gestão de obras
│   ├── equipamentos/          # Gestão de equipamentos
│   ├── financeiro/            # Módulo financeiro
│   ├── manutencao/            # Histórico de manutenções
│   ├── nr12_checklist/        # Sistema NR12
│   ├── orcamentos/            # Gestão de orçamentos
│   └── ordens_servico/        # Ordens de serviço
├── media/                     # Arquivos de mídia
│   └── qr_codes/             # QR codes gerados
├── staticfiles/              # Arquivos estáticos
└── logs/                     # Logs da aplicação
```

## 🔐 Segurança

### Autenticação
- Token-based authentication
- Permissões por grupo de usuário
- Sessões seguras

### API Security
- Rate limiting
- CORS configurado
- Headers de segurança
- Validação de entrada

### Dados Sensíveis
- Senhas hasheadas
- Dados encriptados
- Logs sanitizados
- Backup seguro

## 📈 Monitoramento

### Logs
```bash
# Ver logs em tempo real
docker-compose logs -f web

# Logs específicos
docker-compose logs celery
docker-compose logs nginx
```

### Métricas
- Health check endpoint: `/health/`
- Métricas do sistema via dashboard
- Alertas automáticos por email/Telegram

### Backup
```bash
# Backup manual
python manage.py sistema_mandacaru backup

# Backup automático (Celery)
# Configurado para executar diariamente às 2h
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Email**: suporte@mandacaru.com
- **Telegram**: @MandacaruBot
- **Documentação**: [docs.mandacaru.com](https://docs.mandacaru.com)

## 🎯 Roadmap

### v1.1 (Próxima versão)
- [ ] App mobile nativo
- [ ] Integração com ERP externos
- [ ] Relatórios avançados em PDF
- [ ] Dashboard em tempo real com WebSockets

### v1.2 (Futuro)
- [ ] IA para previsão de manutenções
- [ ] Integração com IoT de equipamentos
- [ ] Multi-tenant para várias empresas
- [ ] API pública para terceiros

---

**Desenvolvido com ❤️ para otimizar a gestão de equipamentos pesados**