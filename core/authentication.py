import os
import json
import logging
import firebase_admin
from firebase_admin import auth, credentials
from ninja.security import HttpBearer
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger(__name__)


def initialize_firebase():
    """Inicializa o SDK Admin do Firebase se ainda não tiver sido inicializado."""
    if firebase_admin._apps:
        return

    # 1. Tenta carregar credenciais em formato JSON bruto (variável de ambiente)
    cred_json = getattr(settings, "FIREBASE_CREDENTIALS_JSON", None) or os.getenv(
        "FIREBASE_CREDENTIALS_JSON"
    )
    if cred_json:
        try:
            cred_dict = (
                json.loads(cred_json) if isinstance(cred_json, str) else cred_json
            )
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            logger.info(
                "Firebase Admin SDK inicializado via JSON de variáveis de ambiente."
            )
            return
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase via JSON: {e}")

    # 2. Tenta carregar arquivo local (caminho em settings)
    cred_path = getattr(
        settings, "FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json"
    )
    if os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK inicializado via arquivo: {cred_path}")
            return
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo de credenciais {cred_path}: {e}")

    # 3. Fallback para Application Default Credentials (GCP / Firebase Hosting)
    try:
        firebase_admin.initialize_app()
        logger.info(
            "Firebase Admin SDK inicializado via Application Default Credentials."
        )
    except Exception as e:
        logger.critical(f"Falha total ao inicializar Firebase Admin SDK: {e}")


# Executa a inicialização ao carregar o módulo
initialize_firebase()


class FirebaseHttpBearer(HttpBearer):
    def authenticate(self, request, token: str):
        """
        Intercepta o cabeçalho 'Authorization: Bearer <TOKEN>',
        valida o JWT com o Firebase Admin SDK e retorna/cria o User no Django ORM.
        """
        if not token:
            return None

        try:
            # Valida o token JWT vindo do cliente
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token.get("uid")

            if not uid:
                return None

            email = decoded_token.get("email", "")
            display_name = decoded_token.get("name", "")

            # Obtém ou cria o usuário correspondente no Django ORM
            user, created = User.objects.get_or_create(
                username=uid,
                defaults={
                    "email": email,
                    "first_name": display_name[:30] if display_name else "",
                },
            )

            # Atualiza o e-mail local se tiver mudado no Firebase
            if not created and user.email != email and email:
                user.email = email
                user.save(update_fields=["email"])

            return user

        except auth.ExpiredIdTokenError:
            logger.warning("Token do Firebase expirado.")
            return None
        except auth.InvalidIdTokenError as e:
            logger.warning(f"Token do Firebase inválido: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na autenticação Firebase: {e}")
            return None
