# ================================================================
# Script PowerShell para configurar o Bot Telegram no Windows
# Salve como: setup_bot.ps1
# Execute: .\setup_bot.ps1
# ================================================================

Write-Host "🤖 CONFIGURANDO BOT TELEGRAM MANDACARU" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Criar estrutura de diretórios
Write-Host "`n📁 Criando estrutura de diretórios..." -ForegroundColor Yellow

$directories = @(
    "backend\apps\bot_telegram",
    "backend\apps\bot_telegram\management",
    "backend\apps\bot_telegram\management\commands",
    "backend\apps\bot_telegram\handlers",
    "backend\apps\bot_telegram\utils",
    "backend\apps\bot_telegram\commands",
    "backend\apps\bot_telegram\tests"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "   ✅ $dir" -ForegroundColor Green
}

# Criar arquivos __init__.py
Write-Host "`n📄 Criando arquivos __init__.py..." -ForegroundColor Yellow

$initFiles = @(
    "backend\apps\bot_telegram\__init__.py",
    "backend\apps\bot_telegram\management\__init__.py",
    "backend\apps\bot_telegram\management\commands\__init__.py",
    "backend\apps\bot_telegram\handlers\__init__.py",
    "backend\apps\bot_telegram\utils\__init__.py",
    "backend\apps\bot_telegram\commands\__init__.py",
    "backend\apps\bot_telegram\tests\__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -ItemType File -Path $file -Force | Out-Null
    Write-Host "   ✅ $file" -ForegroundColor Green
}

# Criar arquivo de configuração
Write-Host "`n📝 Criando arquivo config.py..." -ForegroundColor Yellow

$configContent = @'
# backend/apps/bot_telegram/config.py
from django.conf import settings
import os

# Token do bot
BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN'))

# URLs
API_BASE_URL = getattr(settings, 'API_BASE_URL', 'http://127.0.0.1:8000/api')
BASE_URL = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')

# Configurações de sessão
SESSION_TIMEOUT_HOURS = getattr(settings, 'SESSION_TIMEOUT_HOURS', 24)

# IDs de administradores
ADMIN_IDS = getattr(settings, 'ADMIN_IDS', [])
'@

Set-Content -Path "backend\apps\bot_telegram\config.py" -Value $configContent -Encoding UTF8
Write-Host "   ✅ config.py criado" -ForegroundColor Green

# Criar arquivo .env.example se não existir
if (-not (Test-Path ".env")) {
    Write-Host "`n📝 Criando arquivo .env..." -ForegroundColor Yellow
    
    $envContent = @'
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Telegram Bot
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_BOT_USERNAME=MandacarusmBot
API_BASE_URL=http://127.0.0.1:8000/api
SESSION_TIMEOUT_HOURS=24
ADMIN_IDS=SEU_ID_TELEGRAM

# URLs
BASE_URL=http://127.0.0.1:8000
'@
    
    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
    Write-Host "   ✅ .env criado (configure seu token!)" -ForegroundColor Yellow
}

# Verificar se o ambiente virtual existe
Write-Host "`n🐍 Verificando ambiente virtual..." -ForegroundColor Yellow

if (-not (Test-Path "venv")) {
    Write-Host "   ⚠️ Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   ✅ Ambiente virtual criado" -ForegroundColor Green
}

# Ativar ambiente virtual e instalar dependências
Write-Host "`n📦 Instalando dependências..." -ForegroundColor Yellow
Write-Host "   Execute manualmente:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   pip install -r requirements.txt" -ForegroundColor White
Write-Host "   pip install python-telegram-bot pyzbar opencv-python pillow redis" -ForegroundColor White

# Criar arquivo de requisitos do bot
$requirementsBot = @'
# Bot Telegram
python-telegram-bot==20.7

# Leitura de QR Code
pyzbar==0.1.9
opencv-python==4.8.1.78
Pillow==10.1.0
qrcode==7.4.2

# Cache/Sessions
redis==5.0.1

# Async
aiohttp==3.9.1
asgiref==3.7.2

# Utils
numpy==1.24.3
psutil==5.9.6
'@

Set-Content -Path "requirements_bot.txt" -Value $requirementsBot -Encoding UTF8
Write-Host "`n   ✅ requirements_bot.txt criado" -ForegroundColor Green

# Instruções finais
Write-Host "`n✅ SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Ative o ambiente virtual:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "`n2. Instale as dependências:" -ForegroundColor White
Write-Host "   pip install -r requirements_bot.txt" -ForegroundColor Cyan
Write-Host "`n3. Configure o token no arquivo .env:" -ForegroundColor White
Write-Host "   TELEGRAM_BOT_TOKEN=seu_token_aqui" -ForegroundColor Cyan
Write-Host "`n4. Execute as migrações:" -ForegroundColor White
Write-Host "   python manage.py migrate" -ForegroundColor Cyan
Write-Host "`n5. Crie dados de teste:" -ForegroundColor White
Write-Host "   python manage.py setup_nr12" -ForegroundColor Cyan
Write-Host "   python manage.py criar_operadores_demo" -ForegroundColor Cyan
Write-Host "`n6. Inicie o bot:" -ForegroundColor White
Write-Host "   python manage.py start_telegram_bot --debug" -ForegroundColor Cyan

# Criar um arquivo batch para facilitar
$batchContent = @'
@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Iniciando bot...
python manage.py start_telegram_bot --debug
pause
'@

Set-Content -Path "start_bot.bat" -Value $batchContent -Encoding ASCII
Write-Host "`n💡 Dica: Use 'start_bot.bat' para iniciar rapidamente!" -ForegroundColor Yellow