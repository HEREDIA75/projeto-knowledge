import os
import sys
from firebase_functions import https_fn

# 1. Insere o diretório raiz do projeto no início do PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Configura a variável de ambiente das configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 3. Inicializa as aplicações do Django para evitar inconsistências no Cold Start
import django

django.setup()

import serverless_wsgi
from core.wsgi import application


@https_fn.on_request()
def app(req: https_fn.Request) -> https_fn.Response:
    """Entry point da Cloud Function que redireciona requisições HTTP para a aplicação Django WSGI."""
    return serverless_wsgi.handle_request(application, req)
