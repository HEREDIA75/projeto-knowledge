from typing import List, Optional
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from ninja import Router

from core.authentication import FirebaseHttpBearer
from .models import TransacaoFinanceira, ContaBancaria
from .schemas import (
    ContaBancariaInSchema,
    ContaBancariaOutSchema,
    TransacaoInSchema,
    TransacaoOutSchema,
    TransacaoUpdateStatusSchema,
    DashboardOutSchema,
)
from modules.financeiro.tasks import gerar_relatorio_excel_task

router = Router(tags=["Financeiro / ERP"])


# ==========================================
# ENDPOINTS: CONTA BANCÁRIA (CRUD)
# ==========================================


@router.get("/contas", response=List[ContaBancariaOutSchema], auth=FirebaseHttpBearer())
def listar_contas(request):
    """Lista todas as contas bancárias cadastras."""
    return ContaBancaria.objects.all()


@router.post("/contas", response=ContaBancariaOutSchema, auth=FirebaseHttpBearer())
def criar_conta(request, payload: ContaBancariaInSchema):
    """Cadastra uma nova conta bancária."""
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    conta = ContaBancaria.objects.create(**data)
    return conta


@router.put(
    "/contas/{conta_id}", response=ContaBancariaOutSchema, auth=FirebaseHttpBearer()
)
def atualizar_conta(request, conta_id: int, payload: ContaBancariaInSchema):
    """Atualiza os dados de uma conta bancária."""
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    for attr, value in data.items():
        setattr(conta, attr, value)
    conta.save()
    return conta


@router.delete("/contas/{conta_id}", auth=FirebaseHttpBearer())
def deletar_conta(request, conta_id: int):
    """Remove uma conta bancária."""
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    conta.delete()
    return {"sucesso": True, "mensagem": "Conta bancária removida com sucesso."}


# ==========================================
# ENDPOINT: DASHBOARD FINANCEIRO
# ==========================================


@router.get("/dashboard", response=DashboardOutSchema, auth=FirebaseHttpBearer())
def dashboard_financeiro(request):
    """Retorna os totais de receitas, despesas e saldo geral do usuário autenticado."""
    qs = TransacaoFinanceira.objects.filter(usuario=request.auth)

    # Calculando totais com status PAGO
    total_receitas = qs.filter(tipo="RECEITA", status="PAGO").aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    total_despesas = qs.filter(tipo="DESPESA", status="PAGO").aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")

    # Calculando pendências
    total_pendente_receber = qs.filter(tipo="RECEITA", status="PENDENTE").aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")
    total_pendente_pagar = qs.filter(tipo="DESPESA", status="PENDENTE").aggregate(
        total=Sum("valor")
    )["total"] or Decimal("0.00")

    saldo_geral = total_receitas - total_despesas

    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo_geral": saldo_geral,
        "total_pendente_receber": total_pendente_receber,
        "total_pendente_pagar": total_pendente_pagar,
    }


# ==========================================
# ENDPOINTS: TRANSAÇÕES FINANCEIRAS
# ==========================================


@router.post("/transacoes", response=TransacaoOutSchema, auth=FirebaseHttpBearer())
def criar_transacao(request, payload: TransacaoInSchema):
    """Cria uma nova transação financeira associada ao usuário autenticado."""
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()

    conta_id = data.pop("conta_id", None)
    conta = None
    if conta_id:
        conta = get_object_or_404(ContaBancaria, id=conta_id)

    transacao = TransacaoFinanceira.objects.create(
        usuario=request.auth, conta=conta, **data
    )
    return transacao


@router.get("/transacoes", response=List[TransacaoOutSchema], auth=FirebaseHttpBearer())
def listar_transacoes(
    request, tipo: Optional[str] = None, status: Optional[str] = None
):
    """Lista as transações do usuário, com filtros opcionais por tipo e status."""
    queryset = TransacaoFinanceira.objects.filter(usuario=request.auth)
    if tipo:
        queryset = queryset.filter(tipo=tipo.upper())
    if status:
        queryset = queryset.filter(status=status.upper())
    return queryset


@router.patch(
    "/transacoes/{transacao_id}/status",
    response=TransacaoOutSchema,
    auth=FirebaseHttpBearer(),
)
def atualizar_status_transacao(
    request, transacao_id: int, payload: TransacaoUpdateStatusSchema
):
    """
    Atualiza o status de uma transação (ex: PENDENTE -> PAGO).
    Aciona automaticamente a atualização do saldo da conta bancária via signal.
    """
    transacao = get_object_or_404(
        TransacaoFinanceira, id=transacao_id, usuario=request.auth
    )
    transacao.status = payload.status.upper()
    if payload.data_pagamento:
        transacao.data_pagamento = payload.data_pagamento
    transacao.save()
    return transacao


@router.post("/relatorios/solicitar", auth=None)
def solicitar_relatorio(request):
    """Dispara a tarefa assíncrona no Celery para geração do relatório em Excel."""
    user_id = getattr(request.user, "id", None) or 1

    task = gerar_relatorio_excel_task.delay(user_id=user_id)
    return {
        "task_id": task.id,
        "mensagem": "Processamento do relatório iniciado com sucesso!",
    }
