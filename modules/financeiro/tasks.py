import logging
from decimal import Decimal
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from .models import TransacaoFinanceira

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def gerar_relatorio_excel_task(self, user_id: int = None):
    """
    Gera um relatório financeiro em segundo plano otimizado.
    Executado assincronamente via Celery.
    """
    try:
        queryset = TransacaoFinanceira.objects.all()
        username = "Anônimo / Teste"

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                logger.info(
                    f"Iniciando geração de relatório para o usuário: {user.email}"
                )
                queryset = queryset.filter(usuario=user)
                username = user.username
            except User.DoesNotExist:
                # Fallback seguro: pega o primeiro superusuário se o ID não existir
                user = User.objects.filter(is_superuser=True).first()
                if user:
                    queryset = queryset.filter(usuario=user)
                    username = f"{user.username} (Fallback Superuser)"
                else:
                    logger.error(
                        f"Usuário id {user_id} e nenhum superuser encontrados."
                    )
                    return {"error": "Usuário não encontrado"}
        else:
            logger.info(
                "Iniciando geração de relatório geral (sem usuário específico)."
            )

        # Soma performática direto no SGBD
        zero = Decimal("0.00")
        totais = queryset.aggregate(
            receitas=Coalesce(
                Sum("valor", filter=Q(tipo="RECEITA")),
                zero,
                output_field=DecimalField(),
            ),
            despesas=Coalesce(
                Sum("valor", filter=Q(tipo="DESPESA")),
                zero,
                output_field=DecimalField(),
            ),
        )

        total_receitas = totais["receitas"]
        total_despesas = totais["despesas"]

        resumo = {
            "usuario": username,
            "total_transacoes": queryset.count(),
            "receitas": float(total_receitas),
            "despesas": float(total_despesas),
            "saldo": float(total_receitas - total_despesas),
            "gerado_em": timezone.now().isoformat(),
        }

        logger.info("Relatório financeiro gerado com sucesso!")
        return resumo

    except Exception as exc:
        logger.error(f"Erro ao gerar relatório: {exc}")
        raise self.retry(exc=exc)


@shared_task
def processar_fechamento_mensal():
    """Atualiza transações vencidas de forma assíncrona."""
    logger.info("Executando rotina de fechamento financeiro mensal...")
    hoje = timezone.now().date()

    total_atualizadas = TransacaoFinanceira.objects.filter(
        data_vencimento__lt=hoje, status="PENDENTE"
    ).update(status="ATRASADO")

    logger.info(f"Total de {total_atualizadas} transações marcadas como ATRASADO.")
    return f"{total_atualizadas} transações atualizadas."
