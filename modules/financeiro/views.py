from decimal import Decimal
from typing import List, Optional

from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema

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

# Router unificado
router = Router(tags=["Financeiro"])


# Schemas Adicionais do Módulo
class MensagemStatusSchema(Schema):
    status: str
    mensagem: str


class RelatorioSolicitadoSchema(Schema):
    task_id: str
    mensagem: str


# ==========================================
# ENDPOINT RAIZ DO MÓDULO (Evita 404 em /api/financeiro/)
# ==========================================


@router.get("", response=MensagemStatusSchema)
@router.get("/", response=MensagemStatusSchema)
def resumo_financeiro_raiz(request):
    """Endpoint de status do módulo financeiro."""
    return {
        "status": "online",
        "mensagem": "Módulo Financeiro e DRE ativo com sucesso.",
    }


# ==========================================
# ENDPOINTS: CONTA BANCÁRIA
# ==========================================


@router.get("/contas", response=List[ContaBancariaOutSchema], auth=FirebaseHttpBearer())
def listar_contas(request):
    return ContaBancaria.objects.all()


@router.post("/contas", response=ContaBancariaOutSchema, auth=FirebaseHttpBearer())
def criar_conta(request, payload: ContaBancariaInSchema):
    return ContaBancaria.objects.create(**payload.model_dump())


@router.put(
    "/contas/{conta_id}", response=ContaBancariaOutSchema, auth=FirebaseHttpBearer()
)
def atualizar_conta(request, conta_id: int, payload: ContaBancariaInSchema):
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    for attr, value in payload.model_dump().items():
        setattr(conta, attr, value)
    conta.save()
    return conta


@router.delete("/contas/{conta_id}", auth=FirebaseHttpBearer())
def deletar_conta(request, conta_id: int):
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    conta.delete()
    return {"sucesso": True, "mensagem": "Conta bancária removida com sucesso."}


# ==========================================
# ENDPOINT: DASHBOARD FINANCEIRO
# ==========================================


@router.get("/dashboard", response=DashboardOutSchema, auth=FirebaseHttpBearer())
def dashboard_financeiro(request):
    zero = Decimal("0.00")

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


@router.post("/transacoes", response=TransacaoOutSchema, auth=FirebaseHttpBearer())
def criar_transacao(request, payload: TransacaoInSchema):
    data = payload.model_dump()
    conta_id = data.pop("conta_id", None)
    conta = get_object_or_404(ContaBancaria, id=conta_id) if conta_id else None
    return TransacaoFinanceira.objects.create(usuario=request.auth, conta=conta, **data)


@router.get("/transacoes", response=List[TransacaoOutSchema], auth=FirebaseHttpBearer())
def listar_transacoes(
    request, tipo: Optional[str] = None, status: Optional[str] = None
):
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


# Rota para disparo assíncrono de relatório via Celery
@router.post("/relatorios/solicitar", response=RelatorioSolicitadoSchema)
def solicitar_relatorio(request):
    user_id = None
    if hasattr(request, "auth") and request.auth:
        user_id = getattr(request.auth, "id", None)

    if not user_id and hasattr(request, "user") and request.user.is_authenticated:
        user_id = request.user.id

    # Dispara a tarefa garantindo que user_id seja serializável (ou None)
    task = gerar_relatorio_excel_task.delay(user_id=user_id)

    return {
        "task_id": str(task.id),
        "mensagem": "Processamento do relatório iniciado com sucesso!",
    }
