#!/usr/bin/env python3
# check_and_create_apps.py - Verifica e cria apps que faltam

import os
import sys

# Lista de apps esperados
EXPECTED_APPS = [
    'authentication',
    'dashboard', 
    'nr12_checklist',
    'equipamentos',
    'clientes',
    'empreendimentos',
    'operadores',
    'almoxarifado',
    'financeiro',
    'manutencao',
    'ordens_servico',
    'orcamentos',
    'fornecedor',
    'relatorios',
    'cliente_portal',
    'core',  # Para comandos de gerenciamento
]

def check_app_exists(app_name):
    """Verifica se um app existe"""
    app_path = os.path.join('backend', 'apps', app_name)
    return os.path.exists(app_path)

def create_app_structure(app_name):
    """Cria a estrutura básica de um app Django"""
    app_path = os.path.join('backend', 'apps', app_name)
    
    # Criar diretório do app
    os.makedirs(app_path, exist_ok=True)
    
    # Criar __init__.py
    open(os.path.join(app_path, '__init__.py'), 'a').close()
    
    # Criar models.py
    models_content = '''from django.db import models

# Create your models here.
'''
    with open(os.path.join(app_path, 'models.py'), 'w') as f:
        f.write(models_content)
    
    # Criar views.py
    views_content = '''from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

# Create your views here.
'''
    with open(os.path.join(app_path, 'views.py'), 'w') as f:
        f.write(views_content)
    
    # Criar urls.py
    urls_content = '''from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
'''
    with open(os.path.join(app_path, 'urls.py'), 'w') as f:
        f.write(urls_content)
    
    # Criar apps.py
    apps_content = f'''from django.apps import AppConfig

class {app_name.title().replace("_", "")}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.{app_name}'
'''
    with open(os.path.join(app_path, 'apps.py'), 'w') as f:
        f.write(apps_content)
    
    # Criar admin.py
    admin_content = '''from django.contrib import admin

# Register your models here.
'''
    with open(os.path.join(app_path, 'admin.py'), 'w') as f:
        f.write(admin_content)
    
    # Criar diretório migrations
    migrations_path = os.path.join(app_path, 'migrations')
    os.makedirs(migrations_path, exist_ok=True)
    open(os.path.join(migrations_path, '__init__.py'), 'a').close()
    
    print(f"✅ App '{app_name}' criado com sucesso!")

def create_management_commands_dir():
    """Cria estrutura para comandos de gerenciamento"""
    # Criar diretório para comandos no app core
    core_path = os.path.join('backend', 'apps', 'core')
    management_path = os.path.join(core_path, 'management')
    commands_path = os.path.join(management_path, 'commands')
    
    os.makedirs(commands_path, exist_ok=True)
    
    # Criar __init__.py em cada diretório
    for path in [core_path, management_path, commands_path]:
        init_file = os.path.join(path, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
    
    print("✅ Estrutura de comandos de gerenciamento criada!")

def main():
    print("🔍 Verificando e criando apps Django...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Execute este script no diretório raiz do projeto Django!")
        sys.exit(1)
    
    # Criar diretório backend/apps se não existir
    apps_dir = os.path.join('backend', 'apps')
    if not os.path.exists(apps_dir):
        os.makedirs(apps_dir)
        open(os.path.join(apps_dir, '__init__.py'), 'a').close()
        print("✅ Diretório backend/apps criado!")
    
    # Verificar e criar cada app
    apps_missing = []
    apps_existing = []
    
    for app_name in EXPECTED_APPS:
        if check_app_exists(app_name):
            apps_existing.append(app_name)
        else:
            apps_missing.append(app_name)
    
    # Mostrar status
    print(f"\n📊 Apps existentes ({len(apps_existing)}):")
    for app in apps_existing:
        print(f"  ✅ {app}")
    
    if apps_missing:
        print(f"\n❌ Apps faltando ({len(apps_missing)}):")
        for app in apps_missing:
            print(f"  ❌ {app}")
        
        # Perguntar se deseja criar
        response = input("\n🤔 Deseja criar os apps que faltam? (s/n): ")
        if response.lower() == 's':
            print("\n🔨 Criando apps...")
            for app_name in apps_missing:
                create_app_structure(app_name)
            
            # Criar estrutura de comandos
            create_management_commands_dir()
            
            print(f"\n✅ {len(apps_missing)} apps criados com sucesso!")
            print("\n📝 Próximos passos:")
            print("1. Adicione os apps ao INSTALLED_APPS em settings.py")
            print("2. Execute: python manage.py makemigrations")
            print("3. Execute: python manage.py migrate")
    else:
        print("\n✅ Todos os apps esperados já existem!")
        
        # Verificar estrutura de comandos
        if not os.path.exists(os.path.join('backend', 'apps', 'core', 'management', 'commands')):
            print("\n🔨 Criando estrutura de comandos de gerenciamento...")
            create_management_commands_dir()

if __name__ == "__main__":
    main()
    