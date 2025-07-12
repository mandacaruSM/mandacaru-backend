
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery não instalado, continuar sem ele
    __all__ = ()
    pass