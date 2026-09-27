from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from ninja import Schema
from pydantic import ConfigDict, Field

# Tipo literal para garantir integridade do tipo de transação
TipoTransacao = Literal["RECEITA", "DESPESA"]
StatusTransacao = Literal["PENDENTE", "PAGO", "CANCELADO"]


class ContaBancariaInSchema(Schema):
    nome: str = Field(..., min_length=1, max_length=100)
    saldo_atual: Decimal = Field(default=Decimal("0.00"), decimal_places=2)


class ContaBancariaOutSchema(Schema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    saldo_atual: Decimal


class TransacaoInSchema(Schema):
    descricao: str = Field(..., min_length=1)
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    tipo: TipoTransacao
    status: Optional[StatusTransacao] = "PENDENTE"
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None


class TransacaoOutSchema(Schema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: str
    valor: Decimal
    tipo: str
    status: str
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    criado_em: datetime


class BaixarLancamentoSchema(Schema):
    """Schema específico para a requisição do endpoint POST /lancamentos/{id}/baixar/"""

    conta_id: int
    data_pagamento: Optional[date] = None


class TransacaoUpdateStatusSchema(Schema):
    status: StatusTransacao
    data_pagamento: Optional[date] = None


class DashboardOutSchema(Schema):
    model_config = ConfigDict(from_attributes=True)

    total_receitas: Decimal
    total_despesas: Decimal
    saldo_geral: Decimal
    total_pendente_receber: Decimal
    total_pendente_pagar: Decimal
