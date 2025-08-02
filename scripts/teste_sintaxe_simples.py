# ================================================================
# TESTE SIMPLES DE SINTAXE
# Execute: python teste_sintaxe_simples.py
# ================================================================

import ast
import sys

def verificar_sintaxe_arquivo(caminho_arquivo):
    """Verifica se um arquivo Python tem sintaxe válida"""
    print(f"🔍 Verificando sintaxe: {caminho_arquivo}")
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        # Tentar compilar o código
        ast.parse(conteudo)
        print("✅ Sintaxe válida!")
        return True
        
    except SyntaxError as e:
        print(f"❌ ERRO DE SINTAXE:")
        print(f"   Linha {e.lineno}: {e.text}")
        print(f"   Erro: {e.msg}")
        return False
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")
        return False

def main():
    print("🚀 TESTE DE SINTAXE - Arquivos Python")
    print("=" * 40)
    
    # Lista de arquivos para verificar
    arquivos = [
        'backend/apps/nr12_checklist/serializers.py',
        'backend/apps/nr12_checklist/urls.py',
        'backend/apps/nr12_checklist/viewsets.py',
        'backend/urls.py'
    ]
    
    todos_ok = True
    
    for arquivo in arquivos:
        if not verificar_sintaxe_arquivo(arquivo):
            todos_ok = False
        print()  # Linha em branco
    
    if todos_ok:
        print("🎯 RESULTADO: ✅ Todos os arquivos têm sintaxe válida!")
        print("\n💡 Próximo passo: python manage.py runserver")
    else:
        print("🎯 RESULTADO: ❌ Há erros de sintaxe nos arquivos!")
        print("\n🔧 Corrija os erros antes de continuar")

if __name__ == "__main__":
    main()