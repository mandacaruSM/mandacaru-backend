# ================================================================
# SCRIPT POWERSHELL PARA CRIAR TODOS OS APPS
# Salve como: criar_apps.ps1 e execute: .\criar_apps.ps1
# ================================================================

# Função para criar um app completo
function Create-DjangoApp {
    param(
        [string]$AppName,
        [string]$VerboseName
    )
    
    $AppPath = "backend\apps\$AppName"
    
    # Criar diretório do app
    New-Item -ItemType Directory -Path $AppPath -Force
    New-Item -ItemType Directory -Path "$AppPath\migrations" -Force
    
    # Arquivo __init__.py
    New-Item -ItemType File -Path "$AppPath\__init__.py" -Force
    New-Item -ItemType File -Path "$AppPath\migrations\__init__.py" -Force
    
    # Arquivo apps.py
    $AppsContent = @"
from django.apps import AppConfig

class $($AppName.Replace('_', '').Substring(0,1).ToUpper() + $AppName.Replace('_', '').Substring(1))Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.$AppName'
    verbose_name = '$VerboseName'
"@
    Set-Content -Path "$AppPath\apps.py" -Value $AppsContent
    
    # Arquivo models.py
    $ModelsContent = @"
from django.db import models

# Models serão adicionados depois
"@
    Set-Content -Path "$AppPath\models.py" -Value $ModelsContent
    
    # Arquivo views.py
    $ViewsContent = @"
from django.shortcuts import render

# Views serão adicionadas depois
"@
    Set-Content -Path "$AppPath\views.py" -Value $ViewsContent
    
    # Arquivo admin.py
    $AdminContent = @"
from django.contrib import admin

# Admin será adicionado depois
"@
    Set-Content -Path "$AppPath\admin.py" -Value $AdminContent
    
    # Arquivo tests.py
    $TestsContent = @"
from django.test import TestCase

# Tests serão adicionados depois
"@
    Set-Content -Path "$AppPath\tests.py" -Value $TestsContent
    
    # Arquivo urls.py
    $UrlsContent = @"
from django.urls import path

urlpatterns = [
    # URLs serão adicionadas depois
]
"@
    Set-Content -Path "$AppPath\urls.py" -Value $UrlsContent
    
    # Arquivo serializers.py (para apps que usam DRF)
    $SerializersContent = @"
from rest_framework import serializers

# Serializers serão adicionados depois
"@
    Set-Content -Path "$AppPath\serializers.py" -Value $SerializersContent
    
    Write-Host "✅ App '$AppName' criado com sucesso!" -ForegroundColor Green
}

# Criar todos os apps necessários
Write-Host "🚀 Criando apps do Django..." -ForegroundColor Yellow

Create-DjangoApp -AppName "auth_cliente" -VerboseName "Autenticação de Clientes"
Create-DjangoApp -AppName "nr12_checklist" -VerboseName "Checklists NR12"
Create-DjangoApp -AppName "cliente_portal" -VerboseName "Portal do Cliente"
Create-DjangoApp -AppName "bot_telegram" -VerboseName "Bot Telegram"

# Criar arquivo bot.py específico para o bot_telegram
$BotContent = @"
# Bot Telegram será implementado aqui
"@
Set-Content -Path "backend\apps\bot_telegram\bot.py" -Value $BotContent

Write-Host "✅ Todos os apps foram criados com sucesso!" -ForegroundColor Green
Write-Host "📝 Agora você pode adicionar os apps ao INSTALLED_APPS no settings.py" -ForegroundColor Cyan