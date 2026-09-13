from ninja.security import HttpBearer
from firebase_admin import auth as firebase_auth
from ninja.errors import HttpError


class FirebaseAuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Valida o Token JWT enviado no Header Authorization: Bearer <token>
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token
        except Exception:
            raise HttpError(
                401, "Token de autenticação do Firebase inválido ou expirado."
            )
