from django.conf import settings
from django.db import models


class TransacaoFinanceira(models.Model):
    TIPO_CHOICES = [
        ("RECEITA", "Receita"),
        ("DESPESA", "Despesa"),
    ]

    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("PAGO", "Pago"),
        ("ATRASADO", "Atrasado"),
        ("CANCELADO", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transacoes",
    )
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDENTE")
    data_vencimento = models.DateField(null=True, blank=True)
    data_pagamento = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "financeiro_transacao"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.tipo})"
