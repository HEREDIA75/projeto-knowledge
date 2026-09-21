from decimal import Decimal
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from ninja import Router, Schema

from .models import ContaBancaria, TransacaoFinanceira

router = Router(tags=["Financeiro"])

# -----------------------------------------------------------------------------
# Schemas Pydantic
# -----------------------------------------------------------------------------


class ContaBancariaSchema(Schema):
    id: int
    nome: str
    saldo_atual: Decimal


class ContaBancariaCreateSchema(Schema):
    nome: str
    saldo_inicial: Decimal = Decimal("0.00")


class LancamentoFinanceiroSchema(Schema):
    id: int
    descricao: str
    tipo: str
    valor: Decimal
    status: str
    conta_id: Optional[int] = None
    data_vencimento: Optional[str] = None
    data_pagamento: Optional[str] = None


class LancamentoFinanceiroCreateSchema(Schema):
    descricao: str
    tipo: str
    valor: Decimal
    conta_id: Optional[int] = None
    status: Optional[str] = "PENDENTE"
    data_vencimento: Optional[str] = None


class DashboardFinanceiroSchema(Schema):
    total_receitas_mes: Decimal
    total_despesas_mes: Decimal
    saldo_previsto: Decimal
    saldo_real_contas: Decimal
    contas_vencidas_count: int


# -----------------------------------------------------------------------------
# Endpoints: Contas Bancárias
# -----------------------------------------------------------------------------


@router.get("/contas/", response=List[ContaBancariaSchema])
def listar_contas(request):
    return ContaBancaria.objects.all()


@router.post("/contas/", response=ContaBancariaSchema)
def criar_conta(request, payload: ContaBancariaCreateSchema):
    conta = ContaBancaria.objects.create(
        nome=payload.nome, saldo_atual=payload.saldo_inicial
    )
    return conta


@router.get("/contas/{conta_id}/", response=ContaBancariaSchema)
def obter_conta(request, conta_id: int):
    return get_object_or_404(ContaBancaria, id=conta_id)


# -----------------------------------------------------------------------------
# Endpoints: Lançamentos
# -----------------------------------------------------------------------------


@router.get("/lancamentos/", response=List[LancamentoFinanceiroSchema])
def listar_lancamentos(
    request,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    conta_id: Optional[int] = None,
):
    qs = TransacaoFinanceira.objects.all().order_by("-criado_em")
    if tipo:
        qs = qs.filter(tipo=tipo.upper())
    if status:
        qs = qs.filter(status=status.upper())
    if conta_id:
        qs = qs.filter(conta_id=conta_id)
    return qs


@router.post("/lancamentos/", response=LancamentoFinanceiroSchema)
def criar_lancamento(request, payload: LancamentoFinanceiroCreateSchema):
    conta = None
    if payload.conta_id:
        conta = get_object_or_404(ContaBancaria, id=payload.conta_id)

    # Atribui o usuário logado ou o fallback de desenvolvimento
    user = getattr(request, "user", None)
    if not hasattr(user, "pk") or not user.pk:
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.first()

    lancamento = TransacaoFinanceira.objects.create(
        usuario=user,
        conta=conta,
        descricao=payload.descricao,
        tipo=payload.tipo.upper(),
        valor=payload.valor,
        status=payload.status.upper(),
        data_vencimento=payload.data_vencimento,
    )
    return lancamento


@router.post(
    "/lancamentos/{lancamento_id}/baixar/", response=LancamentoFinanceiroSchema
)
def baixar_lancamento(request, lancamento_id: int):
    lancamento = get_object_or_404(TransacaoFinanceira, id=lancamento_id)
    lancamento.status = "PAGO"
    lancamento.data_pagamento = timezone.now().date()
    lancamento.save()
    return lancamento


# -----------------------------------------------------------------------------
# Endpoint: Dashboard
# -----------------------------------------------------------------------------


@router.get("/dashboard/", response=DashboardFinanceiroSchema)
def obter_dashboard(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)

    receitas = TransacaoFinanceira.objects.filter(
        tipo="RECEITA", criado_em__gte=inicio_mes, status__in=["PAGO", "PENDENTE"]
    ).aggregate(total=Sum("valor"))["total"] or Decimal("0.00")

    despesas = TransacaoFinanceira.objects.filter(
        tipo="DESPESA", criado_em__gte=inicio_mes, status__in=["PAGO", "PENDENTE"]
    ).aggregate(total=Sum("valor"))["total"] or Decimal("0.00")

    saldo_real = ContaBancaria.objects.aggregate(total=Sum("saldo_atual"))[
        "total"
    ] or Decimal("0.00")

    vencidas_count = TransacaoFinanceira.objects.filter(
        tipo="DESPESA", status="PENDENTE", data_vencimento__lt=hoje
    ).count()

    return {
        "total_receitas_mes": receitas,
        "total_despesas_mes": despesas,
        "saldo_previsto": receitas - despesas,
        "saldo_real_contas": saldo_real,
        "contas_vencidas_count": vencidas_count,
    }
