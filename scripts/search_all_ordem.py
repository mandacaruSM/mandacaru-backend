# ===============================================
# SCRIPT: Encontrar todas as referências incorretas a 'ordem'
# ===============================================

import os
import re

def buscar_referencias_ordem():
    """Busca todas as referências ao campo 'ordem' no código"""
    
    print("🔍 BUSCANDO TODAS AS REFERÊNCIAS A 'ordem'")
    print("=" * 60)
    
    # Diretórios para buscar
    diretorios = [
        "backend/apps/nr12_checklist/",
        "backend/apps/operadores/",
        "backend/apps/equipamentos/",
    ]
    
    # Padrões para buscar
    padroes = [
        r"order_by\(['\"]ordem['\"]",
        r"\.ordem\b",
        r"['\"]ordem['\"]\s*:",
        r"ordem\s*=",
        r"checklist\.itens\..*ordem",
        r"ItemChecklistRealizado.*ordem"
    ]
    
    resultados = []
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            continue
            
        print(f"\n📁 Buscando em: {diretorio}")
        
        for root, dirs, files in os.walk(diretorio):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            conteudo = f.read()
                            linhas = conteudo.split('\n')
                            
                            for i, linha in enumerate(linhas, 1):
                                for padrao in padroes:
                                    if re.search(padrao, linha, re.IGNORECASE):
                                        resultado = {
                                            'arquivo': filepath,
                                            'linha': i,
                                            'codigo': linha.strip(),
                                            'padrao': padrao
                                        }
                                        resultados.append(resultado)
                                        print(f"   🎯 {os.path.basename(filepath)}:{i} - {linha.strip()}")
                    
                    except Exception as e:
                        print(f"   ❌ Erro ao ler {filepath}: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"   Total de referências encontradas: {len(resultados)}")
    
    if resultados:
        print(f"\n🛠️  ARQUIVOS QUE PRECISAM SER CORRIGIDOS:")
        arquivos_unicos = set(r['arquivo'] for r in resultados)
        for arquivo in sorted(arquivos_unicos):
            print(f"   📝 {arquivo}")
            
        print(f"\n⚠️  CORREÇÕES NECESSÁRIAS:")
        for i, resultado in enumerate(resultados, 1):
            print(f"   {i}. {os.path.basename(resultado['arquivo'])}:{resultado['linha']}")
            print(f"      ANTES: {resultado['codigo']}")
            
            # Sugerir correção
            codigo_corrigido = resultado['codigo']
            codigo_corrigido = re.sub(r"order_by\(['\"]ordem['\"]\)", "order_by('item_padrao__ordem')", codigo_corrigido)
            codigo_corrigido = re.sub(r"\.ordem\b", ".item_padrao.ordem", codigo_corrigido)
            codigo_corrigido = re.sub(r"['\"]ordem['\"]\s*:", "'item_padrao__ordem':", codigo_corrigido)
            
            if codigo_corrigido != resultado['codigo']:
                print(f"      DEPOIS: {codigo_corrigido}")
            else:
                print(f"      ⚠️  REMOVER ESTA LINHA (campo não existe no modelo)")
            print()
    
    return resultados

def verificar_modelo_itemchecklistrealizado():
    """Verifica os campos reais do modelo"""
    
    print(f"\n🔍 VERIFICANDO MODELO ItemChecklistRealizado")
    print("=" * 50)
    
    try:
        # Tentar importar e inspecionar o modelo
        import sys
        sys.path.append('.')
        
        from backend.apps.nr12_checklist.models import ItemChecklistRealizado
        
        # Obter campos do modelo
        campos = [field.name for field in ItemChecklistRealizado._meta.fields]
        
        print("✅ Campos disponíveis no modelo:")
        for campo in sorted(campos):
            print(f"   - {campo}")
        
        if 'ordem' in campos:
            print(f"\n✅ Campo 'ordem' EXISTE no modelo")
        else:
            print(f"\n❌ Campo 'ordem' NÃO EXISTE no modelo")
            print(f"   Para ordenar, use: item_padrao__ordem")
    
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {e}")

def main():
    """Função principal"""
    print("🕵️ DETECTIVE DE BUGS - CAMPO 'ordem'")
    print("=" * 60)
    
    # 1. Buscar referências
    resultados = buscar_referencias_ordem()
    
    # 2. Verificar modelo
    verificar_modelo_itemchecklistrealizado()
    
    # 3. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    if resultados:
        print(f"   ❌ Encontradas {len(resultados)} referências incorretas")
        print(f"   🛠️  Corrija TODAS as referências listadas acima")
        print(f"   🔄 Depois reinicie o Django e teste novamente")
    else:
        print(f"   ✅ Nenhuma referência incorreta encontrada")
        print(f"   🤔 O erro pode estar em outro lugar")

if __name__ == "__main__":
    main()