# ================================================================
# Dockerfile para Mandacaru ERP Backend
# ================================================================

FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p media/qr_codes/{checklists,equipamentos,temp} \
    && mkdir -p staticfiles \
    && mkdir -p logs

# Configurar permissões
RUN chmod +x manage.py

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando padrão
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "backend.wsgi:application"]