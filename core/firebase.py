import json
import logging
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# Caminho para a raiz do projeto (projeto-knowledge/)
BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BASE_DIR / "firebase-credentials.json"


def initialize_firebase():
    """Inicializa o SDK do Firebase Admin.

    Ordem de prioridade:
    1. Variável de ambiente FIREBASE_CREDENTIALS_JSON (Render / Produção)
    2. Arquivo JSON na raiz (Ambiente Local)
    3. Application Default Credentials (ADC)
    """
    if firebase_admin._apps:
        return

    # 1. Tenta carregar do Render / Produção via variável de ambiente contendo o JSON string
    creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if creds_json:
        try:
            cred_dict = json.loads(creds_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print(
                "✓ Firebase inicializado via variável de ambiente (FIREBASE_CREDENTIALS_JSON)"
            )
            return
        except Exception as e:
            print(f"⚠️ Erro ao processar FIREBASE_CREDENTIALS_JSON: {e}")

    # 2. Tenta carregar do arquivo JSON local (Desenvolvimento)
    if CREDENTIALS_PATH.exists():
        try:
            cred = credentials.Certificate(str(CREDENTIALS_PATH))
            firebase_admin.initialize_app(cred)
            print(f"✓ Firebase inicializado via arquivo local: {CREDENTIALS_PATH.name}")
            return
        except Exception as e:
            print(f"⚠️ Erro ao ler arquivo de credenciais ({CREDENTIALS_PATH}): {e}")

    # 3. Fallback para ADC / Variável GOOGLE_APPLICATION_CREDENTIALS
    try:
        firebase_admin.initialize_app()
        print("✓ Firebase inicializado via ADC / Variável de Ambiente")
    except Exception as e:
        print(f"⚠️ Não foi possível inicializar o Firebase: {e}")


def get_firestore_client():
    """Retorna o cliente do Firestore ou None caso haja falha."""
    initialize_firebase()

    if not firebase_admin._apps:
        return None

    try:
        return firestore.client()
    except Exception as e:
        print(f"⚠️ Erro ao conectar ao cliente do Firestore: {e}")
        return None


# Instância global exportada para o projeto
db = get_firestore_client()
