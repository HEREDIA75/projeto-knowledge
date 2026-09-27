import uuid
from django.db import models
from django.conf import settings
from modules.estoque.models import Produto


class Venda(models.Model):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente de Sincronização/Fiscal"),
        ("CONCLUIDA", "Concluída"),
        ("CANCELADA", "Cancelada"),
    ]

    TIPO_EMISSAO_CHOICES = [
        ("1", "Normal (Online)"),
        ("9", "Contingência Offline NFC-e"),
    ]

    # O id vem do PDV (UUID gerado no navegador/IndexedDB)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vendas"
    )
    data_venda = models.DateTimeField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDENTE")

    # Controle Fiscal (NFC-e)
    tipo_emissao = models.CharField(
        max_length=1, choices=TIPO_EMISSAO_CHOICES, default="1"
    )
    chave_acesso = models.CharField(max_length=44, blank=True, null=True, unique=True)
    xml_assinado = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda {self.id} - R$ {self.valor_total}"


class ItemVenda(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
