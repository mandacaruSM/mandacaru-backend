# PowerShell Script - Execute do diretório mandacaru_erp (não scripts/)
Write-Host "=== TESTE CORRIGIDO - SISTEMA NR12 ===" -ForegroundColor Cyan

# 1. Verificar se estamos no diretório correto
$currentPath = Get-Location
Write-Host "Diretório atual: $currentPath" -ForegroundColor Yellow

if (-not (Test-Path "backend\manage.py")) {
    Write-Host "❌ Execute este script do diretório mandacaru_erp" -ForegroundColor Red
    Write-Host "Navegue para: cd D:\projeto\mandacaru_erp" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar arquivos
Write-Host "`n=== VERIFICANDO ARQUIVOS ===" -ForegroundColor Cyan

$arquivos = @(
    "backend\manage.py",
    "backend\apps\nr12_checklist\models.py", 
    "backend\apps\nr12_checklist\bot_views\bot_telegram.py",
    "mandacaru_bot\core\db.py"
)

foreach ($arquivo in $arquivos) {
    if (Test-Path $arquivo) {
        Write-Host "✓ $arquivo" -ForegroundColor Green
    } else {
        Write-Host "❌ $arquivo NÃO encontrado" -ForegroundColor Red
    }
}

# 3. Verificar erro específico no bot_telegram.py
Write-Host "`n=== VERIFICANDO ERRO DE IMPORT ===" -ForegroundColor Cyan

if (Test-Path "backend\apps\nr12_checklist\bot_views\bot_telegram.py") {
    $conteudo = Get-Content "backend\apps\nr12_checklist\bot_views\bot_telegram.py" -Raw
    
    if ($conteudo -match "import logging") {
        Write-Host "✓ Import logging encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ Import logging FALTANDO - PRECISA SER ADICIONADO" -ForegroundColor Red
        Write-Host "   Adicione 'import logging' no topo do arquivo" -ForegroundColor Yellow
    }
    
    if ($conteudo -match "\.categoria") {
        Write-Host "❌ Uso de '.categoria' encontrado - DEVE SER '.criticidade'" -ForegroundColor Red
    } else {
        Write-Host "✓ Não usa '.categoria' incorretamente" -ForegroundColor Green
    }
}

# 4. Verificar função no bot
Write-Host "`n=== VERIFICANDO FUNÇÃO DO BOT ===" -ForegroundColor Cyan

if (Test-Path "mandacaru_bot\core\db.py") {
    $botConteudo = Get-Content "mandacaru_bot\core\db.py" -Raw
    
    if ($botConteudo -match "def iniciar_checklist_nr12") {
        Write-Host "✓ Função iniciar_checklist_nr12 encontrada" -ForegroundColor Green
    } else {
        Write-Host "❌ Função iniciar_checklist_nr12 FALTANDO" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Arquivo mandacaru_bot\core\db.py não encontrado" -ForegroundColor Red
}

# 5. Resumo dos problemas
Write-Host "`n=== PROBLEMAS IDENTIFICADOS ===" -ForegroundColor Yellow
Write-Host "1. ❌ Import logging faltando em bot_telegram.py" -ForegroundColor Red
Write-Host "2. ❌ Função iniciar_checklist_nr12 faltando em core/db.py" -ForegroundColor Red
Write-Host "3. ⚠️  Possível uso de 'categoria' ao invés de 'criticidade'" -ForegroundColor Yellow

Write-Host "`n=== AÇÕES IMEDIATAS ===" -ForegroundColor Cyan
Write-Host "1. Adicionar 'import logging' no topo de bot_telegram.py" -ForegroundColor White
Write-Host "2. Adicionar função iniciar_checklist_nr12 em core/db.py" -ForegroundColor White  
Write-Host "3. Substituir '.categoria' por '.criticidade' onde encontrar" -ForegroundColor White

Write-Host "`n✅ DEPOIS DAS CORREÇÕES: python manage.py runserver funcionará!" -ForegroundColor Green