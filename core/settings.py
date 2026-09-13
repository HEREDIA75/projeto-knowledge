"""
Django settings for core project (Knowledge Platform).
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Segurança e Ambiente
# -----------------------------------------------------------------------------
SECRET_KEY = config(
    "SECRET_KEY", default="django-insecure-chave-temporaria-desenvolvimento-123"
)
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="127.0.0.1,localhost,.web.app,.firebaseapp.com", cast=Csv()
)

# -----------------------------------------------------------------------------
# Aplicações
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "storages",
    "modules",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
    )
}

# -----------------------------------------------------------------------------
# Validação de Senhas & Internacionalização
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Configuração de Storages (Estáticos e Mídia)
# -----------------------------------------------------------------------------
USE_GCP_STORAGE = config("USE_GCP_STORAGE", default=not DEBUG, cast=bool)

# Estáticos Padrão
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# Mídia Padrão (Local)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Se ativado via .env ou em Produção (DEBUG=False)
if USE_GCP_STORAGE:
    GS_BUCKET_NAME = config(
        "GS_BUCKET_NAME", default="meu-app-django-bc95f.appspot.com"
    )
    GS_CREDENTIALS_FILE = BASE_DIR / "credentials" / "firebase-key.json"

    options = {
        "bucket_name": GS_BUCKET_NAME,
        "location": "media",
    }

    if GS_CREDENTIALS_FILE.exists():
        from google.oauth2 import service_account

        options["credentials"] = service_account.Credentials.from_service_account_file(
            GS_CREDENTIALS_FILE
        )

    STORAGES["default"] = {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": options,
    }
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"

# -----------------------------------------------------------------------------
# CORS & Outras Configurações
# -----------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=DEBUG, cast=bool)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
