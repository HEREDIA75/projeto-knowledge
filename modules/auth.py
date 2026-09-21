import logging
from firebase_admin import auth
from ninja.security import HttpBearer
from django.contrib.auth.models import User
from modules.firebase import initialize_firebase

logger = logging.getLogger(__name__)

# Garante que o SDK foi inicializado
initialize_firebase()


class FirebaseHttpBearer(HttpBearer):
    def authenticate(self, request, token: str):
        """
        Intercepta o cabeçalho 'Authorization: Bearer <TOKEN>',
        valida o JWT com o Firebase Admin SDK e retorna/cria o User no Django.
        """
        if not token:
            return None

        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token.get("uid")

            if not uid:
                return None

            email = decoded_token.get("email", "")
            display_name = decoded_token.get("name", "")

            user, created = User.objects.get_or_create(
                username=uid,
                defaults={
                    "email": email,
                    "first_name": display_name[:30] if display_name else "",
                },
            )

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
            logger.error(f"Erro na autenticação Firebase: {e}")
            return None
