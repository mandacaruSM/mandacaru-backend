#### File: backend/apps/bot_telegram/tests/test_handlers.py
import pytest
from backend.apps.bot_telegram.ext import MessageHandler, CallbackQueryHandler
from backend.apps.bot_telegram.handlers.message import text_handler
from backend.apps.bot_telegram.handlers.photo import photo_handler
from backend.apps.bot_telegram.handlers.callback import callback_handler


def test_text_handler():
    assert isinstance(text_handler, MessageHandler)


def test_photo_handler():
    assert isinstance(photo_handler, MessageHandler)


def test_callback_handler():
    assert isinstance(callback_handler, CallbackQueryHandler)