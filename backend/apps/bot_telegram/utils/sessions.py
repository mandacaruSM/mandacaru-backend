### File: backend/apps/bot_telegram/utils/sessions.py
from typing import Dict


_sessions: Dict[int, dict] = {}

def init_session(chat_id: int, data: dict):
    _sessions[chat_id] = data

def get_session(chat_id: int) -> dict:
    return _sessions.get(chat_id, {})

def clear_session(chat_id: int):
    _sessions.pop(chat_id, None)