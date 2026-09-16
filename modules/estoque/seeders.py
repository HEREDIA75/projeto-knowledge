from decimal import Decimal
from django.utils import timezone
from modules.financeiro.models import Categoria, ContaBancaria, Transacao


def run_seeder():
    # 1. Criar Categorias
    cat_receita, _ = Categoria.objects.get_or_create(
        nome="Vendas de Serviços", tipo="RECEITA"
    )
    cat_despesa, _ = Categoria.objects.get_or_create(
        nome="Infraestrutura / Cloud", tipo="DESPESA"
    )

    # 2. Criar Conta Bancária
    conta, _ = ContaBancaria.objects.get_or_create(
        nome="Banco Principal", defaults={"saldo_atual": Decimal("10000.00")}
    )

    # 3. Criar Transações de Teste
    Transacao.objects.create(
        conta=conta,
        categoria=cat_receita,
        descricao="Pagamento Cliente A",
        valor=Decimal("2500.00"),
        tipo="RECEITA",
        data_transacao=timezone.now(),
    )

    Transacao.objects.create(
        conta=conta,
        categoria=cat_despesa,
        descricao="Servidor AWS",
        valor=Decimal("450.00"),
        tipo="DESPESA",
        data_transacao=timezone.now(),
    )

    print("Seeder executado com sucesso!")
