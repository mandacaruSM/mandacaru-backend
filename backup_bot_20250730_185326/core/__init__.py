# mandacaru_bot/core/__init__.py
# Arquivo para resolver imports

try:
    from .session import *
    from .db import *
    from .config import *
    from .utils import *
except ImportError as e:
    print(f"Aviso: Erro de import em core: {e}")