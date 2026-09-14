from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.financeiro"  # <--- Deve conter o prefixo "modules."
