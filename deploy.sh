#!/usr/bin/env bash

# Interrompe a execução caso ocorra algum erro
set -e

echo "🚀 Iniciando processo de automação e deploy..."

# 1. Executa o collectstatic usando o venv principal da raiz
echo "📦 Executando collectstatic no venv principal..."
python manage.py collectstatic --noinput

# 2. Sincroniza o requirements.txt na pasta functions sem alterar o ambiente da raiz
echo "⚙️ Atualizando dependências internas do Firebase Functions..."
if [ -d "functions" ]; then
    (
        cd functions
        if [ -d "venv" ]; then
            source venv/bin/activate
            # Garante a instalação de todas as libs necessárias para a Function rodar no GCP
            pip install -q django-storages google-cloud-storage firebase-functions functions-framework serverless-wsgi Django python-decouple
            pip freeze > requirements.txt
        else
            echo "⚠️ Aviso: venv interno em 'functions/' não encontrado."
        fi
    )
fi

# 3. Menu de deploy
echo ""
echo "Selecione o tipo de deploy:"
echo "1) Deploy completo (Hosting + Cloud Functions) [Exige Plano Blaze]"
echo "2) Apenas Hosting (Estáticos) [Plano Spark Gratuito]"
read -p "Opção (1 ou 2): " opcao

if [ "$opcao" == "1" ]; then
    echo "🔥 Executando deploy completo (firebase deploy)..."
    firebase deploy
elif [ "$opcao" == "2" ]; then
    echo "🌐 Executando deploy de arquivos estáticos (firebase deploy --only hosting)..."
    firebase deploy --only hosting
else
    echo "❌ Opção inválida. Operação cancelada."
    exit 1
fi

echo "✅ Processo concluído com sucesso!"