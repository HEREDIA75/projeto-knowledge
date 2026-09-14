#!/usr/bin/env bash

# Encerra processos filhos caso o script seja cancelado (Ctrl+C)
trap "kill 0" EXIT

echo "🚀 Iniciando ambiente de desenvolvimento..."

# 1. Verifica/Inicia o Redis em segundo plano se não estiver rodando
if ! pgrep -x "redis-server" > /dev/null
then
    echo "📦 Iniciando Redis Server..."
    redis-server --daemonize yes
else
    echo "⚡ Redis já está em execução."
fi

# 2. Inicia o Celery Worker
echo "⚙️  Iniciando Celery Worker..."
celery -A core worker --loglevel=info &

# 3. Inicia o Servidor de Desenvolvimento do Django Ninja
echo "🌐 Iniciando Django Ninja (runserver)..."
python manage.py runserver 0.0.0.0:8000

wait