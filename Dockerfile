FROM python:3.12-slim

# Evita a gravação de ficheiros .pyc e força o output sem buffer nos logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Configura espelhos alternativos do Debian, ativa retentativas no apt e instala as dependências
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . /app/