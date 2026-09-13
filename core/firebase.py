import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from django.conf import settings

# Caminho para as credenciais baixadas
cred_path = os.path.join(settings.BASE_DIR, "firebase-credentials.json")

if not firebase_admin._apps:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback para ambiente de producao usando variaveis de ambiente
        firebase_admin.initialize_app()

db = firestore.client() if firebase_admin._apps else None
