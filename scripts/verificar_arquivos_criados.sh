#!/bin/bash

echo "🔍 VERIFICANDO ARQUIVOS CRIADOS"
echo "=============================="

# Verificar se os arquivos foram criados
arquivos=(
    "backend/apps/nr12_checklist/views_bot.py"
    "backend/apps/equipamentos/views_bot.py"
    "backend/apps/operadores/views_bot.py"
    "backend/apps/core/management/commands/corrigir_bot.py"
    "backend/urls_bot_patch.py"
    "scripts/testar_bot_apis.py"
)

for arquivo in "${arquivos[@]}"; do
    if [ -f "$arquivo" ]; then
        echo "✅ $arquivo"
        echo "   📊 $(wc -l < "$arquivo") linhas"
    else
        echo "❌ $arquivo (não encontrado)"
    fi
done

echo ""
echo "📋 CONTEÚDO DO PATCH:"
echo "===================="
if [ -f "backend/urls_bot_patch.py" ]; then
    cat backend/urls_bot_patch.py
else
    echo "❌ Arquivo de patch não encontrado"
fi