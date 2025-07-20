#### File: backend/apps/bot_telegram/tests/test_commands.py
import pytest
from telegram.ext import CommandHandler
from backend.apps.bot_telegram.commands.start import start_handler
from backend.apps.bot_telegram.commands.help import help_handler
from backend.apps.bot_telegram.commands.status import status_handler
from backend.apps.bot_telegram.commands.logout import logout_handler


def test_start_handler():
    assert isinstance(start_handler, CommandHandler)
    assert 'start' in start_handler.command


def test_help_handler():
    assert isinstance(help_handler, CommandHandler)
    assert 'help' in help_handler.command


def test_status_handler():
    assert isinstance(status_handler, CommandHandler)
    assert 'status' in status_handler.command


def test_logout_handler():
    assert isinstance(logout_handler, CommandHandler)
    assert 'logout' in logout_handler.command