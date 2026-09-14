from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal


class TransacaoInSchema(BaseModel):
    descricao: str
    valor: Decimal
    tipo: str  # RECEITA ou DESPESA
    data_pagamento: date


class TransacaoOutSchema(BaseModel):
    id: int
    descricao: str
    valor: Decimal
    tipo: str
    data_pagamento: date
    criado_em: datetime
