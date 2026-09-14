from typing import List, Optional
from ninja import Router
from core.authentication import FirebaseHttpBearer
from .models import TransacaoFinanceira
from .schemas import TransacaoInSchema, TransacaoOutSchema
from modules.financeiro.tasks import gerar_relatorio_excel_task

router = Router(tags=["Financeiro / ERP"])


@router.post("/transacoes", response=TransacaoOutSchema, auth=FirebaseHttpBearer())
def criar_transacao(request, payload: TransacaoInSchema):
    """Cria uma nova transação financeira associada ao usuário autenticado."""
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    transacao = TransacaoFinanceira.objects.create(usuario=request.auth, **data)
    return transacao


@router.get("/transacoes", response=List[TransacaoOutSchema], auth=FirebaseHttpBearer())
def listar_transacoes(request, tipo: Optional[str] = None):
    """Lista as transações do usuário, com filtro opcional por tipo (RECEITA/DESPESA)."""
    queryset = TransacaoFinanceira.objects.filter(usuario=request.auth)
    if tipo:
        queryset = queryset.filter(tipo=tipo.upper())
    return queryset


@router.post("/relatorios/solicitar", auth=None)
def solicitar_relatorio(request):
    """Dispara a tarefa assíncrona no Celery para geração do relatório em Excel."""
    user_id = getattr(request.user, "id", None) or 1

    task = gerar_relatorio_excel_task.delay(user_id=user_id)
    return {
        "task_id": task.id,
        "mensagem": "Processamento do relatório iniciado com sucesso!",
    }
