#!/usr/bin/env bash

# Encerra a execução caso algum comando falhe inesperadamente
set -e

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Portas padrão utilizadas pelo Firebase Emulator (Hosting, Functions, UI, Hub, Logging)
PORTS=(5001 5005 4005 4400 4500)

echo "🧹 1. Verificando e liberando portas ocupadas..."
for PORT in "${PORTS[@]}"; do
  # Localiza PIDs usando fuser/lsof
  PIDS=$(lsof -t -i:"$PORT" 2>/dev/null || true)
  if [ -n "$PIDS" ]; then
    echo "   ⚠️ Encerrando processos na porta $PORT (PIDs: $PIDS)..."
    kill -9 $PIDS 2>/dev/null || true
  fi
done

echo "📦 2. Sincronizando arquivos estáticos do Django..."
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    "$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/manage.py" collectstatic --noinput --verbosity 0
fi

echo "⚙️ 3. Validando o SDK na pasta functions..."
if [ -d "$PROJECT_ROOT/functions" ]; then
    (
        cd "$PROJECT_ROOT/functions"
        # Cria o venv interno se não existir
        if [ ! -d "venv" ]; then
            echo "   🔨 Criando venv interno em functions/..."
            python3 -m venv venv
        fi
        
        # Ativa o venv de functions em subshell para instalar o SDK necessário
        source venv/bin/activate
        if ! python -c "import firebase_functions" 2>/dev/null; then
            echo "   📥 Instalando dependências ausentes no venv de functions..."
            pip install -q firebase-functions functions-framework serverless-wsgi Django python-decouple
        fi
    )
fi

echo "🚀 4. Iniciando o Firebase Emulator..."
echo ""
firebase emulators:start