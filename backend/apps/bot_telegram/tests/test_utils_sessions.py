#### File: backend/apps/bot_telegram/tests/test_utils_sessions.py
from backend.apps.bot_telegram.utils.sessions import init_session, get_session, clear_session


def test_session_lifecycle():
    chat_id = 12345
    # Ensure clear state
    clear_session(chat_id)
    assert get_session(chat_id) == {}

    data = {'key': 'value'}
    init_session(chat_id, data)
    assert get_session(chat_id) == data

    clear_session(chat_id)
    assert get_session(chat_id) == {}