# =====================
# core/db.py (corrigido)
# =====================

import httpx
from core.config import API_BASE_URL
from datetime import datetime

async def buscar_operador_por_nome(nome):
    url = f"{API_BASE_URL}/operadores/?search={nome}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json().get('results', [])
        return []

async def validar_data_nascimento(id_operador, data_digitada):
    url = f"{API_BASE_URL}/operadores/{id_operador}/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data_api = response.json().get("data_nascimento")
            try:
                # Converte entrada do usuário
                dia, mes, ano = map(int, data_digitada.split("/"))
                data_usuario = f"{ano:04d}-{mes:02d}-{dia:02d}"
                return data_usuario == data_api
            except:
                return False
        return False

async def registrar_chat_id(id_operador, chat_id):
    url = f"{API_BASE_URL}/operadores/{id_operador}/"
    async with httpx.AsyncClient() as client:
        await client.patch(url, json={"chat_id_telegram": chat_id})
