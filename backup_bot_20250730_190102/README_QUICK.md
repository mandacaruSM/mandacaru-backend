# 🚀 Bot Mandacaru - Início Rápido

## ⚡ Configuração em 5 Minutos

### 1. 📦 Setup Automático
```bash
python quick_start.py
```

### 2. 🔑 Configurar Token
1. Abra o Telegram
2. Procure por `@BotFather`
3. Digite `/newbot` e siga as instruções
4. Copie o token para o arquivo `.env`:
```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

### 3. 👤 Configurar Admin
1. Envie mensagem para `@userinfobot`
2. Copie seu ID para o `.env`:
```env
ADMIN_IDS=123456789
```

### 4. 🌐 Verificar API
Certifique-se que o Django está rodando:
```bash
curl http://127.0.0.1:8000/api/operadores/
```

### 5. 🚀 Executar Bot
```bash
python start.py
```

## 🛠️ Se Algo Der Errado

### Diagnóstico Automático
```bash
python diagnose.py
```

### Problemas Comuns

**❌ "TELEGRAM_BOT_TOKEN não encontrado"**
```bash
# Verificar se .env existe e tem o token
cat .env | grep TELEGRAM_BOT_TOKEN
```

**❌ "Erro ao buscar operador"**
```bash
# Verificar se Django está rodando
curl http://127.0.0.1:8000/api/operadores/
```

**❌ "Módulo não encontrado"**
```bash
# Instalar dependências
pip install -r requirements.txt
```

## 📱 Testar o Bot

1. Procure seu bot no Telegram
2. Digite `/start`
3. Informe nome e data de nascimento
4. Use o menu para navegar

## 📋 Comandos Administrativos

- `/admin` - Menu administrativo
- `/status` - Status do sistema
- `/health` - Verificação completa

## 🆘 Suporte

- 📖 **Documentação completa:** `INSTALLATION_GUIDE.md`
- 🔍 **Verificação:** `CHECKLIST.md`
- 🛠️ **Diagnóstico:** `python diagnose.py`

---

**🎯 Meta:** Bot funcionando em menos de 5 minutos!