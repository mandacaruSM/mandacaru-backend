# ===============================================
# SCRIPT DE INSTALAÇÃO RÁPIDA
# scripts/instalar_correcoes.py
# ===============================================

import os
import shutil

def instalar_correcoes():
    """Copia os arquivos de correção para os locais corretos"""
    
    print("📦 INSTALANDO CORREÇÕES DO BOT")
    print("=" * 40)
    
    # Definir caminhos
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    arquivos_correcoes = [
        {
            'origem': 'scripts/bot_checklists.py',
            'destino': 'backend/apps/nr12_checklist/bot_views/bot_checklists.py'
        },
        {
            'origem': 'scripts/views_bot_operadores.py',
            'destino': 'backend/apps/operadores/views_bot.py'
        },
        {
            'origem': 'scripts/views_bot_equipamentos.py',
            'destino': 'backend/apps/equipamentos/views_bot.py'
        },
    ]
    
    for arquivo in arquivos_correcoes:
        origem = os.path.join(base_path, arquivo['origem'])
        destino = os.path.join(base_path, arquivo['destino'])
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        
        # Copiar arquivo
        try:
            shutil.copy2(origem, destino)
            print(f"✅ {arquivo['destino']}")
        except Exception as e:
            print(f"❌ {arquivo['destino']}: {e}")
    
    print("\n🎉 CORREÇÕES INSTALADAS!")
    print("Execute: python manage.py aplicar_correcoes_bot")

if __name__ == "__main__":
    instalar_correcoes()