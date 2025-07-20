# 🤖 Bot Mandacaru

Sistema de automação Telegram para gestão empresarial modular.

## 📋 Funcionalidades

### Módulos Disponíveis
- **📋 Checklist** - Sistema de verificações e inspeções
- **⛽ Abastecimento** - Controle de combustível e gastos
- **🔧 Ordem de Serviço** - Gestão de solicitações de manutenção  
- **💰 Financeiro** - Relatórios e consultas financeiras
- **📱 QR Code** - Geração e leitura de códigos QR

### Recursos do Sistema
- ✅ Autenticação segura por nome + data de nascimento
- 🔐 Sistema de sessões em memória
- 🛡️ Middleware de autorização e logging
- 📊 Painel administrativo completo
- 🎨 Templates padronizados para mensagens
- 🔄 Limpeza automática de sessões
- 📈 Monitoramento de sistema em tempo real

## 🏗️ Arquitetura

```
mandacaru_bot/
├── bot_main/              # Módulo principal
│   ├── main.py           # Inicialização do bot
│   ├── handlers.py       # Handlers de autenticação
│   └── admin_handlers.py # Comandos administrativos
├── bot_checklist/        # Módulo de checklist
├── bot_abastecimento/    # Módulo de abastecimento
├── bot_os/               # Módulo de ordem de serviço
├── bot_financeiro/       # Módulo financeiro
├── bot_qrcode/           # Módulo QR Code
├── core/                 # Núcleo do sistema
│   ├── config.py         # Configurações
│   ├── db.py             # Acesso à API
│   ├── session.py        # Gerenciamento de sessões
│   ├── middleware.py     # Middlewares de autenticação
│   ├── utils.py          # Utilitários gerais
│   └── templates.py      # Templates de mensagens
└── start.py              # Script de inicialização
```

## 🚀 Instalação

### 1. Pré-requisitos
- Python 3.8+
- Token do Bot Telegram
- API do sistema Mandacaru rodando

### 2. Clonar e configurar
```bash
git clone <repository>
cd mandacaru_bot

# Instalar dependências
pip install -r requirements.txt

# Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Configuração do .env
```env
TELEGRAM_TOKEN=seu_token_aqui
API_BASE_URL=http://localhost:8000/api
DEBUG=True
ADMIN_IDS=123456789,987654321
```

### 4. Executar
```bash
python start.py
```

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `TELEGRAM_TOKEN` | Token do bot | Obrigatório |
| `API_BASE_URL` | URL da API | `http://localhost:8000/api` |
| `API_TIMEOUT` | Timeout das requisições | `10` |
| `DEBUG` | Modo debug | `False` |
| `SESSION_TIMEOUT_HOURS` | Expiração de sessão | `24` |
| `ADMIN_IDS` | IDs dos administradores | - |

### Comandos Administrativos

Para usuários com ID em `ADMIN_IDS`:

- `/admin` - Menu administrativo
- `/status` - Status do sistema
- `/stats` - Estatísticas de uso
- `/sessions` - Sessões ativas
- `/cleanup` - Limpar sessões antigas
- `/health` - Verificação de saúde
- `/broadcast` - Mensagem para todos

## 🔐 Autenticação

### Fluxo de Login
1. Usuário envia `/start`
2. Sistema solicita nome completo
3. Busca operador na API por nome
4. Solicita data de nascimento para validação
5. Valida dados na API
6. Registra chat_id e libera acesso

### Middleware de Segurança
- `@require_auth` - Exige autenticação
- `@admin_required` - Exige privilégios admin
- Logging automático de ações

## 📡 Integração com API

### Endpoints Utilizados
- `GET /operadores/?search=nome` - Buscar operador
- `GET /operadores/{id}/` - Dados do operador
- `PATCH /operadores/{id}/` - Atualizar chat_id
- `GET /checklists/` - Listar checklists
- `POST /checklists/` - Criar checklist

### Estrutura de Resposta
```json
{
  "results": [...],
  "count": 100,
  "next": "url",
  "previous": "url"
}
```

## 🛠️ Desenvolvimento

### Adicionar Novo Módulo

1. Criar diretório `bot_novomodulo/`
2. Implementar `handlers.py`:
```python
from core.middleware import require_auth

@require_auth  
async def handler(message, operador=None):
    # Sua lógica aqui
    pass

def register_handlers(dp):
    dp.message.register(handler, F.text == "Comando")
```

3. Registrar em `main.py`:
```python
from bot_novomodulo.handlers import register_handlers as register_novo_handlers
register_novo_handlers(dp)
```

### Templates de Mensagem
```python
from core.templates import MessageTemplates

# Usar templates padronizados
await message.answer(
    MessageTemplates.success_template(
        "Operação Concluída",
        "Dados salvos com sucesso"
    )
)
```

### Validações
```python
from core.utils import Validators

# Validar dados
data = Validators.validar_data("15/03/1990")
cpf_valido = Validators.validar_cpf("123.456.789-00")
```

## 📊 Monitoramento

### Logs
- Arquivo: `logs/bot.log`
- Rotação automática
- Níveis: DEBUG, INFO, WARNING, ERROR

### Métricas Disponíveis
- Sessões ativas
- Usuários autenticados
- Uso de CPU e memória
- Status da API
- Estatísticas por módulo

## 🔄 Deployment

### Desenvolvimento
```bash
python start.py
```

### Produção
```bash
# Com systemd
sudo systemctl start mandacaru-bot

# Com Docker
docker build -t mandacaru-bot .
docker run -d mandacaru-bot
```

### Exemplo Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "start.py"]
```

## 🐛 Troubleshooting

### Problemas Comuns

**Bot não responde**
- Verificar token no .env
- Confirmar que API está rodando
- Checar logs em `logs/bot.log`

**Erro de autenticação**
- Verificar dados do operador na API
- Confirmar formato da data (DD/MM/AAAA)
- Validar se operador existe

**Alta utilização de memória**
- Executar `/cleanup` para limpar sessões
- Verificar número de usuários ativos
- Considerar reduzir `SESSION_TIMEOUT_HOURS`

### Logs Úteis
```bash
# Ver logs em tempo real
tail -f logs/bot.log

# Filtrar erros
grep ERROR logs/bot.log

# Estatísticas de uso
grep "STATS" logs/bot.log
```

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Criar Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja arquivo `LICENSE` para detalhes.

## 📞 Suporte

- 📧 Email: suporte@mandacaru.com
- 💬 Telegram: @suporte_mandacaru
- 🐛 Issues: GitHub Issues

---

Desenvolvido com ❤️ pela equipe Mandacaru