from django.contrib import admin
from .models import ContaBancaria, TransacaoFinanceira


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "saldo_atual")
    search_fields = ("nome",)


@admin.register(TransacaoFinanceira)
class TransacaoFinanceiraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descricao",
        "valor",
        "tipo",
        "status",
        "conta",
        "usuario",
        "criado_em",
    )
    list_filter = ("tipo", "status", "conta")
    search_fields = ("descricao",)
