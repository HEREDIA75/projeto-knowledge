from django.apps import AppConfig


class EstoqueConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.estoque"  # <--- Deve conter o prefixo "modules."
