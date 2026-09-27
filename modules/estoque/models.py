import uuid
from django.db import models


class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_barras = models.CharField(max_length=32, unique=True, db_index=True)
    nome = models.CharField(max_length=150)

    # CORREÇÃO AQUI: max_digits em vez de max_length
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.000
    )

    # Fiscal NFE / NFC-e
    ncm = models.CharField(max_length=8, default="00000000")
    cest = models.CharField(max_length=7, blank=True, null=True)
    cfop = models.CharField(max_length=4, default="5102")

    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo_barras} - {self.nome}"
