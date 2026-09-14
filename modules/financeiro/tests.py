from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from api import api
from financeiro.models import TransacaoFinanceira

User = get_user_model()


class FinanceiroAPITestCase(TestCase):
    def setUp(self):
        # Cria cliente de testes do Django Ninja
        self.client = TestClient(api)

        # Cria usuário fictício no banco de dados de testes
        self.user = User.objects.create_user(
            username="test_firebase_uid_123", email="teste@empresa.com"
        )

    @patch("core.authentication.FirebaseHttpBearer.authenticate")
    def test_criar_transacao_com_sucesso(self, mock_auth):
        # Simula a validação do token Firebase retornando o usuário de testes
        mock_auth.return_value = self.user

        payload = {
            "descricao": "Venda de Licença ERP",
            "valor": "2500.00",
            "tipo": "RECEITA",
            "data_pagamento": "2026-09-15",
        }

        response = self.client.post(
            "/financeiro/transacoes",
            json=payload,
            headers={"HTTP_AUTHORIZATION": "Bearer fake_firebase_token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["descricao"], "Venda de Licença ERP")
        self.assertTrue(TransacaoFinanceira.objects.filter(usuario=self.user).exists())

    @patch("core.authentication.FirebaseHttpBearer.authenticate")
    def test_solicitar_relatorio_celery(self, mock_auth):
        mock_auth.return_value = self.user

        # Simula o disparo da tarefa do Celery sem precisar rodar o Redis durante o teste
        with patch("financeiro.tasks.gerar_relatorio_excel_task.delay") as mock_task:
            mock_task.return_value.id = "mocked-task-uuid-12345"

            response = self.client.post(
                "/financeiro/solicitar-relatorio",
                headers={"HTTP_AUTHORIZATION": "Bearer fake_firebase_token"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["task_id"], "mocked-task-uuid-12345")
            mock_task.assert_called_once_with(self.user.id)
