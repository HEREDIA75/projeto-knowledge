from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


class ContaBancaria(models.Model):
    nome = models.CharField(max_length=100)
    saldo_atual = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"{self.nome} - R$ {self.saldo_atual}"


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
    conta = models.ForeignKey(
        ContaBancaria,
        on_delete=models.CASCADE,
        related_name="transacoes",
        null=True,
        blank=True,
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


@receiver(post_save, sender=TransacaoFinanceira)
def atualizar_saldo_conta(sender, instance, created, **kwargs):
    """
    Atualiza o saldo da conta vinculada apenas quando o status for 'PAGO'.
    """
    if instance.conta and instance.status == "PAGO":
        with transaction.atomic():
            conta = instance.conta
            # Se for uma nova transação ou alteração para PAGO
            if instance.tipo == "RECEITA":
                conta.saldo_atual += instance.valor
            elif instance.tipo == "DESPESA":
                conta.saldo_atual -= instance.valor
            conta.save()
