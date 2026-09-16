from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient

from modules.api import api
from modules.financeiro.models import TransacaoFinanceira, ContaBancaria

User = get_user_model()


class FinanceiroAPITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)

        # Usuário de teste
        self.user = User.objects.create_user(
            id=1, username="test_firebase_uid_123", email="teste@empresa.com"
        )

        # Conta bancária para testes de saldo
        self.conta = ContaBancaria.objects.create(
            nome="Banco do Brasil", saldo_atual=Decimal("1000.00")
        )

    @patch("core.authentication.FirebaseHttpBearer.authenticate")
    def test_criar_transacao_com_sucesso(self, mock_auth):
        mock_auth.return_value = self.user

        payload = {
            "descricao": "Venda de Licença ERP",
            "valor": "2500.00",
            "tipo": "RECEITA",
            "status": "PENDENTE",
            "conta_id": self.conta.id,
            "data_vencimento": "2026-09-30",
        }

        response = self.client.post(
            "/financeiro/transacoes",
            json=payload,
            headers={"Authorization": "Bearer fake_firebase_token"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["descricao"], "Venda de Licença ERP")
        self.assertEqual(data["status"], "PENDENTE")
        self.assertTrue(TransacaoFinanceira.objects.filter(usuario=self.user).exists())

    @patch("core.authentication.FirebaseHttpBearer.authenticate")
    def test_atualizar_status_transacao_e_alterar_saldo(self, mock_auth):
        mock_auth.return_value = self.user

        # Cria transação pendente no banco
        transacao = TransacaoFinanceira.objects.create(
            usuario=self.user,
            conta=self.conta,
            descricao="Pagamento de Serviço",
            valor=Decimal("500.00"),
            tipo="RECEITA",
            status="PENDENTE",
        )

        payload = {
            "status": "PAGO",
            "data_pagamento": "2026-09-15",
        }

        # Atualiza status para PAGO via PATCH
        response = self.client.patch(
            f"/financeiro/transacoes/{transacao.id}/status",
            json=payload,
            headers={"Authorization": "Bearer fake_firebase_token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "PAGO")

        # Garante que o signal incrementou o saldo de R$ 1000.00 para R$ 1500.00
        self.conta.refresh_from_db()
        self.assertEqual(self.conta.saldo_atual, Decimal("1500.00"))

    @patch("core.authentication.FirebaseHttpBearer.authenticate")
    def test_solicitar_relatorio_celery(self, mock_auth):
        mock_auth.return_value = self.user

        with patch(
            "modules.financeiro.tasks.gerar_relatorio_excel_task.delay"
        ) as mock_task:
            mock_task.return_value.id = "mocked-task-uuid-12345"

            response = self.client.post(
                "/financeiro/relatorios/solicitar",
                user=self.user,
                headers={"Authorization": "Bearer fake_firebase_token"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["task_id"], "mocked-task-uuid-12345")
            mock_task.assert_called_once_with(user_id=self.user.id)
