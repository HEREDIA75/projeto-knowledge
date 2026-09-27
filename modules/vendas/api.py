from typing import List
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.security import HttpBearer
from modules.estoque.models import Produto
from modules.vendas.models import Venda, ItemVenda

router = Router(tags=["Vendas PDV"])


class ItemVendaSchema(Schema):
    produto_id: str
    quantidade: float
    preco_unitario: float


class VendaSyncSchema(Schema):
    id: str  # UUID gerado offline pelo IndexedDB
    data_venda: str
    valor_total: float
    tipo_emissao: str = "1"
    itens: List[ItemVendaSchema]


@router.post("/sincronizar")
@transaction.atomic
def sincronizar_vendas_offline(request, payload: List[VendaSyncSchema]):
    vendas_processadas = []

    for v_data in payload:
        # 1. Checagem de Idempotência: Se a venda já foi recebida, ignora a duplicação
        venda_existente = Venda.objects.filter(id=v_data.id).first()
        if venda_existente:
            vendas_processadas.append(
                {"id": str(venda_existente.id), "status": "JA_EXISTIA"}
            )
            continue

        # 2. Cria a Venda no Banco
        venda = Venda.objects.create(
            id=v_data.id,
            usuario=request.user,
            data_venda=v_data.data_venda,
            valor_total=Decimal(str(v_data.valor_total)),
            tipo_emissao=v_data.tipo_emissao,
            status="CONCLUIDA",
        )

        # 3. Processa os Itens e Abate Estoque de forma Atômica
        for item in v_data.itens:
            # Trava o registro do produto para evitar race conditions no estoque
            produto = Produto.objects.select_for_update().get(id=item.produto_id)

            # Baixa de estoque
            produto.quantidade_estoque -= Decimal(str(item.quantidade))
            produto.save()

            # Registra o item
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=Decimal(str(item.quantidade)),
                preco_unitario=Decimal(str(item.preco_unitario)),
                subtotal=Decimal(str(item.quantidade * item.preco_unitario)),
            )

        vendas_processadas.append({"id": str(venda.id), "status": "SUCESSO"})

    return {"status": "ok", "processados": vendas_processadas}
