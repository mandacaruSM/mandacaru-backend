# ✅ Checklist de Verificação - Bot Mandacaru

Use este checklist antes de executar o bot para garantir que tudo está configurado corretamente.

## 📋 Pré-requisitos

### 🐍 Python e Ambiente
- [ ] Python 3.8+ instalado
- [ ] pip funcionando
- [ ] Virtual environment ativado (recomendado)

### 📁 Estrutura de Arquivos
- [ ] Pasta `mandacaru_bot/` na raiz do projeto Django
- [ ] Arquivo `.env` existe e está configurado
- [ ] Diretório `logs/` criado
- [ ] Arquivo `requirements.txt` presente

### 🔧 Configuração

#### Arquivo .env
- [ ] `TELEGRAM_BOT_TOKEN` configurado
- [ ] `API_BASE_URL` configurado (ex: http://127.0.0.1:8000/api)
- [ ] `ADMIN_IDS` configurado com seu ID do Telegram
- [ ] `BASE_URL` configurado para o Django

#### Token do Bot
- [ ] Bot criado no @BotFather
- [ ] Token copiado para o .env
- [ ] Bot está ativo (não deletado)

#### ID de Administrador
- [ ] ID obtido via @userinfobot
- [ ] ID adicionado ao ADMIN_IDS no .env

## 📦 Dependências

### Pacotes Python
- [ ] `aiogram==3.4.1` instalado
- [ ] `httpx==0.26.0` instalado
- [ ] `python-dotenv==1.0.0` instalado
- [ ] `psutil==5.9.8` instalado

Verificar com:
```bash
pip list | grep -E "(aiogram|httpx|python-dotenv|psutil)"
```

## 🌐 API Django

### Endpoints Necessários
- [ ] Django rodando em http://127.0.0.1:8000
- [ ] Endpoint `/api/operadores/` acessível
- [ ] Endpoint `/api/checklists/` acessível
- [ ] CORS configurado se necessário

Testar com:
```bash
curl http://127.0.0.1:8000/api/operadores/
```

### Modelo Operador
- [ ] Campo `chat_id_telegram` existe no modelo
- [ ] Campo `data_nascimento` existe
- [ ] Migração executada
- [ ] Dados de teste existem

## 🧪 Testes Básicos

### Teste de Configuração
```bash
python -c "from core.config import TELEGRAM_TOKEN, API_BASE_URL; print('✅ Config OK' if TELEGRAM_TOKEN and API_BASE_URL else '❌ Config ERRO')"
```

### Teste de Imports
```bash
python -c "from core.session import iniciar_sessao; from core.db import buscar_operador_por_nome; print('✅ Imports OK')"
```

### Teste de API
```bash
python -c "
import asyncio
from core.db import verificar_status_api
result = asyncio.run(verificar_status_api())
print('✅ API OK' if result else '❌ API ERRO')
"
```

## 🚀 Execução

### Métodos de Execução
- [ ] **Opção 1:** `python start.py` funciona
- [ ] **Opção 2:** `python manage.py run_telegram_bot` funciona (Django)

### Verificação de Logs
- [ ] Arquivo `logs/bot.log` está sendo criado
- [ ] Logs mostram "Bot iniciado"
- [ ] Não há erros críticos nos logs

## 📱 Teste do Bot

### Fluxo de Autenticação
- [ ] Bot responde ao `/start`
- [ ] Solicita nome do operador
- [ ] Encontra operador no sistema
- [ ] Solicita data de nascimento
- [ ] Autentica com dados corretos
- [ ] Mostra menu principal

### Comandos Administrativos (para admins)
- [ ] `/admin` mostra menu administrativo
- [ ] `/status` mostra status do sistema
- [ ] `/health` executa verificação de saúde

### Módulos
- [ ] Menu "📋 Checklist" funciona
- [ ] Menu "❓ Ajuda" mostra informações

## 🐛 Solução de Problemas Comuns

### Bot não responde
1. [ ] Verificar se token está correto no .env
2. [ ] Verificar se bot não foi deletado no @BotFather
3. [ ] Verificar logs em `logs/bot.log`

### Erro de autenticação
1. [ ] Verificar se API Django está rodando
2. [ ] Verificar se URL da API está correta
3. [ ] Verificar se operador existe no banco
4. [ ] Verificar formato da data (DD/MM/AAAA)

### Erro de importação
1. [ ] Verificar se está no diretório correto
2. [ ] Verificar se `mandacaru_bot` está no PYTHONPATH
3. [ ] Verificar se todas as dependências estão instaladas

### API não responde
1. [ ] Verificar se Django está rodando
2. [ ] Verificar URL da API no .env
3. [ ] Testar endpoint manualmente com curl
4. [ ] Verificar configuração de CORS

## 📊 Monitoramento

### Logs para Verificar
```bash
# Ver logs em tempo real
tail -f logs/bot.log

# Procurar erros
grep ERROR logs/bot.log

# Ver últimas 50 linhas
tail -50 logs/bot.log
```

### Comandos de Status
- `/status` - Status geral do sistema
- `/stats` - Estatísticas de uso
- `/sessions` - Sessões ativas
- `/health` - Verificação completa

## ✅ Checklist Final

Antes de colocar em produção, verificar:

- [ ] Todos os itens acima estão ✅
- [ ] Bot responde corretamente ao `/start`
- [ ] Autenticação funciona com dados reais
- [ ] Logs estão sendo gerados sem erros
- [ ] Comandos administrativos funcionam
- [ ] Não há vazamentos de memória
- [ ] Performance está adequada

## 📞 Suporte

Se algo não funcionar:

1. 📋 Consulte os logs: `tail -f logs/bot.log`
2. 🧪 Execute os testes de verificação acima
3. 🔍 Verifique a documentação no INSTALLATION_GUIDE.md
4. 💬 Entre em contato com a equipe técnica

---

**🎉 Parabéns!** Se todos os itens estão ✅, seu Bot Mandacaru está pronto para uso!