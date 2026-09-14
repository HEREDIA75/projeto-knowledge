import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TransacaoFinanceira

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def gerar_relatorio_excel_task(self, user_id: int):
    """
    Gera um relatório financeiro em segundo plano para o usuário.
    É executado assincronamente via Celery.
    """
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Iniciando geração de relatório para o usuário: {user.email}")

        # Busca as transações do usuário
        transacoes = TransacaoFinanceira.objects.filter(usuario=user)
        total_receitas = sum(t.valor for t in transacoes if t.tipo == "RECEITA")
        total_despesas = sum(t.valor for t in transacoes if t.tipo == "DESPESA")

        # Simula o tempo de processamento pesado (ex: gerar arquivo Excel/PDF)
        # Em produção, você usaria bibliotecas como pandas, openpyxl ou reportlab
        resumo = {
            "usuario": user.username,
            "total_transacoes": transacoes.count(),
            "receitas": float(total_receitas),
            "despesas": float(total_despesas),
            "saldo": float(total_receitas - total_despesas),
            "gerado_em": timezone.now().isoformat(),
        }

        logger.info(f"Relatório gerado com sucesso para user_id {user_id}")
        return resumo

    except User.DoesNotExist:
        logger.error(f"Usuário id {user_id} não encontrado.")
        return {"error": "Usuário não encontrado"}
    except Exception as exc:
        logger.error(f"Erro ao gerar relatório: {exc}")
        # Tenta novamente a execução caso ocorra um erro temporário
        raise self.retry(exc=exc)


@shared_task
def processar_fechamento_mensal():
    """
    Tarefa agendada (Celery Beat) para rodar no final de cada mês.
    Consolida as transações e atualiza os saldos.
    """
    logger.info("Executando rotina de fechamento financeiro mensal...")

    # Exemplo: Atualiza status de pendências vencidas
    hoje = timezone.now().date()
    transacoes_vencidas = TransacaoFinanceira.objects.filter(
        data_vencimento__lt=hoje, status="PENDENTE"
    )

    total_atualizadas = transacoes_vencidas.update(status="ATRASADO")
    logger.info(f"Total de {total_atualizadas} transações marcadas como ATRASADO.")

    return f"{total_atualizadas} transações atualizadas."
