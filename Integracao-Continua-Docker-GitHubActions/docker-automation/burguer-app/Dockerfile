# ================================
# Etapa 1: Imagem base de build
# ================================
FROM python:3.11-slim AS base

# Definir diretório de trabalho padrão
WORKDIR /app

# Não gerar .pyc e forçar stdout/stderr direto
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependências do sistema (otimizado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# ================================
# Etapa 2: Instalar requirements
# ================================
FROM base AS builder

# Copiar apenas requirements.txt primeiro (cache eficiente)
COPY requirements.txt /app/

# Instalar dependências em cache layer
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# ================================
# Etapa 3: Final image (slim)
# ================================
FROM python:3.11-slim AS final

WORKDIR /app

# Copiar dependências já instaladas do builder
COPY --from=builder /install /usr/local

# Copiar código do microserviço
COPY . /app

# Porta padrão (ajustável no docker-compose)
EXPOSE 5000 5001 5002 5003

# Comando de inicialização
CMD ["python", "app.py"]
