import os
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o app Firebase apenas se ainda não estiver inicializado
if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        try:
            # Tenta inicialização padrão (GCP ADC)
            firebase_admin.initialize_app()
        except Exception as e:
            print(f"Aviso: Firebase não pôde ser inicializado automaticamente: {e}")

# Tenta capturar o cliente do Firestore com segurança
try:
    db = firestore.client() if firebase_admin._apps else None
except Exception as e:
    print(f"Aviso: Firestore não conectado: {e}")
    db = None
