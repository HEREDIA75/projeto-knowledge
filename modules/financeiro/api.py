from decimal import Decimal
from typing import List, Optional

from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router

from core.authentication import FirebaseHttpBearer
from modules.financeiro.tasks import gerar_relatorio_excel_task
from .models import ContaBancaria, TransacaoFinanceira
from .schemas import (
    ContaBancariaInSchema,
    ContaBancariaOutSchema,
    DashboardOutSchema,
    TransacaoInSchema,
    TransacaoOutSchema,
    TransacaoUpdateStatusSchema,
)

# Autenticação global no router
router = Router(tags=["Financeiro"], auth=FirebaseHttpBearer())


# ==========================================
# ENDPOINTS: CONTA BANCÁRIA
# ==========================================


@router.get("/contas", response=List[ContaBancariaOutSchema])
def listar_contas(request):
    return ContaBancaria.objects.all()


@router.post("/contas", response=ContaBancariaOutSchema)
def criar_conta(request, payload: ContaBancariaInSchema):
    return ContaBancaria.objects.create(**payload.model_dump())


@router.put("/contas/{conta_id}", response=ContaBancariaOutSchema)
def atualizar_conta(request, conta_id: int, payload: ContaBancariaInSchema):
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    for attr, value in payload.model_dump().items():
        setattr(conta, attr, value)
    conta.save()
    return conta


@router.delete("/contas/{conta_id}")
def deletar_conta(request, conta_id: int):
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    conta.delete()
    return {"sucesso": True, "mensagem": "Conta bancária removida com sucesso."}


# ==========================================
# ENDPOINT: DASHBOARD FINANCEIRO
# ==========================================


@router.get("/dashboard", response=DashboardOutSchema)
def dashboard_financeiro(request):
    zero = Decimal("0.00")

    # Agregação em 1 query SQL
    totais = TransacaoFinanceira.objects.filter(usuario=request.auth).aggregate(
        receitas=Coalesce(
            Sum("valor", filter=Q(tipo="RECEITA", status="PAGO")),
            zero,
            output_field=DecimalField(),
        ),
        despesas=Coalesce(
            Sum("valor", filter=Q(tipo="DESPESA", status="PAGO")),
            zero,
            output_field=DecimalField(),
        ),
        pendente_receber=Coalesce(
            Sum("valor", filter=Q(tipo="RECEITA", status="PENDENTE")),
            zero,
            output_field=DecimalField(),
        ),
        pendente_pagar=Coalesce(
            Sum("valor", filter=Q(tipo="DESPESA", status="PENDENTE")),
            zero,
            output_field=DecimalField(),
        ),
    )

    total_receitas = totais["receitas"]
    total_despesas = totais["despesas"]

    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_geral": total_receitas - total_despesas,
        "total_pendente_receber": totais["pendente_receber"],
        "total_pendente_pagar": totais["pendente_pagar"],
    }


# ==========================================
# ENDPOINTS: TRANSAÇÕES FINANCEIRAS
# ==========================================


@router.post("/transacoes", response=TransacaoOutSchema)
def criar_transacao(request, payload: TransacaoInSchema):
    data = payload.model_dump()
    conta_id = data.pop("conta_id", None)

    conta = get_object_or_404(ContaBancaria, id=conta_id) if conta_id else None

    return TransacaoFinanceira.objects.create(usuario=request.auth, conta=conta, **data)


@router.get("/transacoes", response=List[TransacaoOutSchema])
def listar_transacoes(
    request, tipo: Optional[str] = None, status: Optional[str] = None
):
    queryset = TransacaoFinanceira.objects.filter(usuario=request.auth)
    if tipo:
        queryset = queryset.filter(tipo=tipo.upper())
    if status:
        queryset = queryset.filter(status=status.upper())
    return queryset


@router.patch("/transacoes/{transacao_id}/status", response=TransacaoOutSchema)
def atualizar_status_transacao(
    request, transacao_id: int, payload: TransacaoUpdateStatusSchema
):
    transacao = get_object_or_404(
        TransacaoFinanceira, id=transacao_id, usuario=request.auth
    )

    novo_status = payload.status.upper()
    transacao.status = novo_status

    if payload.data_pagamento:
        transacao.data_pagamento = payload.data_pagamento
    elif novo_status == "PAGO" and not transacao.data_pagamento:
        transacao.data_pagamento = timezone.now().date()

    transacao.save()
    return transacao


@router.post("/relatorios/solicitar")
def solicitar_relatorio(request):
    user_id = getattr(request.auth, "id", None) or getattr(request.user, "id", None)
    task = gerar_relatorio_excel_task.delay(user_id=user_id)
    return {
        "task_id": task.id,
        "mensagem": "Processamento do relatório iniciado com sucesso!",
    }
