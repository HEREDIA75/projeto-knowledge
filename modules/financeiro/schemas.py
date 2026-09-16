from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from ninja import Schema


class TransacaoInSchema(Schema):
    descricao: str
    valor: Decimal
    tipo: str  # "RECEITA" ou "DESPESA"
    status: Optional[str] = "PENDENTE"  # "PENDENTE", "PAGO", "ATRASADO", "CANCELADO"
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None


class TransacaoOutSchema(Schema):
    id: int
    descricao: str
    valor: Decimal
    tipo: str
    status: str
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    criado_em: datetime


class TransacaoUpdateStatusSchema(Schema):
    """Schema específico para a rota PATCH de atualização de status."""

    status: str  # "PAGO", "CANCELADO", etc.
    data_pagamento: Optional[date] = None


# --- SCHEMAS DE CONTA BANCÁRIA ---
class ContaBancariaInSchema(Schema):
    nome: str
    saldo_atual: Optional[Decimal] = Decimal("0.00")


class ContaBancariaOutSchema(Schema):
    id: int
    nome: str
    saldo_atual: Decimal


# --- SCHEMAS DE TRANSAÇÃO ---
class TransacaoInSchema(Schema):
    descricao: str
    valor: Decimal
    tipo: str  # "RECEITA" ou "DESPESA"
    status: Optional[str] = "PENDENTE"  # "PENDENTE", "PAGO", "ATRASADO", "CANCELADO"
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None


class TransacaoOutSchema(Schema):
    id: int
    descricao: str
    valor: Decimal
    tipo: str
    status: str
    conta_id: Optional[int] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    criado_em: datetime


class TransacaoUpdateStatusSchema(Schema):
    status: str
    data_pagamento: Optional[date] = None


# --- SCHEMA DE DASHBOARD ---
class DashboardOutSchema(Schema):
    total_receitas: Decimal
    total_despesas: Decimal
    saldo_geral: Decimal
    total_pendente_receber: Decimal
    total_pendente_pagar: Decimal
