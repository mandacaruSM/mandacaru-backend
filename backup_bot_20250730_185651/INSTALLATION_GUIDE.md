# 📋 Guia de Instalação - Bot Telegram Mandacaru

Este guia explica como integrar o Bot Telegram com seu sistema Django existente.

## 🔧 Pré-requisitos

- ✅ Sistema Django Mandacaru funcionando
- ✅ Python 3.8+ instalado
- ✅ Token do Bot Telegram (obter no @BotFather)
- ✅ API do Django acessível

## 📦 Instalação

### 1. Estrutura de Diretórios

Coloque a pasta `mandacaru_bot` na raiz do seu projeto Django:

```
mandacaru_erp/
├── manage.py
├── mandacaru_erp/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── apps/
│   ├── operadores/
│   ├── checklists/
│   └── ...
├── mandacaru_bot/          # ← Nova pasta do bot
│   ├── bot_main/
│   ├── core/
│   ├── bot_checklist/
│   └── ...
├── .env
└── requirements.txt
```

### 2. Instalar Dependências

Adicione ao seu `requirements.txt` existente:

```txt
# Bot Telegram
aiogram==3.4.1
httpx==0.26.0
psutil==5.9.8
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Seu arquivo `.env` já existe, apenas adicione estas variáveis:

```env
# Configurações do Bot Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
API_BASE_URL=http://127.0.0.1:8000/api
ADMIN_IDS=123456789,987654321

# Configurações opcionais do bot
BOT_DEBUG=True
SESSION_TIMEOUT_HOURS=24
ITEMS_PER_PAGE=10
```

### 4. Criar Token do Bot

1. Abra o Telegram
2. Procure por `@BotFather`
3. Digite `/newbot`
4. Siga as instruções
5. Copie o token para o `.env`

## 🚀 Executar o Bot

### Opção 1: Como Comando Django (Recomendado)

1. Crie o arquivo `apps/core/management/commands/run_telegram_bot.py` (use o código fornecido)

2. Execute o comando:
```bash
python manage.py run_telegram_bot
```

3. Para modo debug:
```bash
python manage.py run_telegram_bot --debug
```

### Opção 2: Script Standalone

Execute diretamente:
```bash
cd mandacaru_bot
python start.py
```

## 🔧 Configuração da API Django

### 1. Verificar Endpoints Necessários

O bot precisa destes endpoints na sua API:

```python
# urls.py da API
urlpatterns = [
    path('operadores/', views.OperadorListView.as_view()),
    path('operadores/<int:pk>/', views.OperadorDetailView.as_view()),
    path('checklists/', views.ChecklistListView.as_view()),
    path('checklists/<int:pk>/', views.ChecklistDetailView.as_view()),
    path('ordens-servico/', views.OSListView.as_view()),
    path('abastecimentos/', views.AbastecimentoListView.as_view()),
    # ... outros endpoints
]
```

### 2. Adicionar Campo chat_id ao Modelo Operador

```python
# models.py
class Operador(models.Model):
    # ... campos existentes
    chat_id_telegram = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="ID do chat do Telegram"
    )
```

Execute a migração:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Configurar CORS (se necessário)

Se a API estiver em domínio diferente:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]
```

## 🔐 Configurar Administradores

1. Obtenha seu ID do Telegram:
   - Envie uma mensagem para `@userinfobot`
   - Copie o ID numérico

2. Adicione ao `.env`:
```env
ADMIN_IDS=123456789,987654321
```

3. Teste com `/admin` no bot

## 📊 Verificar Funcionamento

### 1. Testar API

```bash
curl http://127.0.0.1:8000/api/operadores/
```

### 2. Testar Bot

1. Inicie o bot
2. No Telegram, procure pelo seu bot
3. Digite `/start`
4. Siga o fluxo de autenticação

### 3. Comandos de Teste

Para administradores:
- `/admin` - Menu administrativo
- `/status` - Status do sistema
- `/health` - Verificação de saúde

## 🚨 Solução de Problemas

### Erro: "TELEGRAM_BOT_TOKEN não encontrado"

**Solução:** Verifique se o token está no `.env` com o nome correto:
```env
TELEGRAM_BOT_TOKEN=1234567890:AABBCCDDEEFFgghhiijjkkllmmnnoopp
```

### Erro: "API não está respondendo"

**Soluções:**
1. Verifique se o Django está rodando
2. Confirme a URL da API no `.env`
3. Teste manualmente: `curl http://127.0.0.1:8000/api/operadores/`

### Bot não responde após /start

**Soluções:**
1. Verifique se existem operadores cadastrados
2. Confirme se o campo `data_nascimento` existe no modelo
3. Veja os logs: `tail -f logs/bot.log`

### Erro de importação de módulos

**Solução:** Verifique se o caminho está correto:
```python
# Se necessário, adicione ao PYTHONPATH
import sys
sys.path.append('/caminho/para/mandacaru_bot')
```

## 📋 Estrutura de Logs

Os logs ficam em:
```
mandacaru_bot/
├── logs/
│   ├── bot.log          # Log principal
│   └── error.log        # Apenas erros
```

Monitorar logs:
```bash
tail -f mandacaru_bot/logs/bot.log
```

## 🔄 Atualização

Para atualizar o bot:

1. Pare o bot (Ctrl+C)
2. Atualize os arquivos
3. Reinstale dependências se necessário
4. Reinicie o bot

## 🚀 Deploy em Produção

### Usando Systemd

1. Crie `/etc/systemd/system/mandacaru-bot.service`:

```ini
[Unit]
Description=Mandacaru Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/mandacaru_erp
Environment=DJANGO_SETTINGS_MODULE=mandacaru_erp.settings
ExecStart=/path/to/venv/bin/python manage.py run_telegram_bot
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Ative o serviço:
```bash
sudo systemctl enable mandacaru-bot
sudo systemctl start mandacaru-bot
```

### Usando Docker

1. Adicione ao seu `Dockerfile`:
```dockerfile
# Instalar dependências do bot
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código do bot
COPY mandacaru_bot/ ./mandacaru_bot/
```

2. Adicione ao `docker-compose.yml`:
```yaml
services:
  telegram-bot:
    build: .
    command: python manage.py run_telegram_bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
      - web
```

## ✅ Checklist Final

- [ ] Bot responde a `/start`
- [ ] Autenticação funciona com dados reais
- [ ] Comandos administrativos funcionam
- [ ] Logs estão sendo gerados
- [ ] API responde corretamente
- [ ] Variáveis de ambiente configuradas
- [ ] Administradores podem usar `/admin`

## 📞 Suporte

Se encontrar problemas:

1. 📋 Verifique os logs em `logs/bot.log`
2. 🔍 Teste a API manualmente
3. 🤖 Confirme o token do bot
4. 📧 Entre em contato com a equipe técnica

---

✨ **Parabéns!** Seu Bot Telegram Mandacaru está configurado e funcionando!