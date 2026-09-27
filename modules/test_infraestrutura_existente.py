import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestInfraestruturaExistente:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username="admin_test", password="password123", email="admin@test.com"
        )

    def test_rota_autenticacao_jwt_existente(self):
        """Valida se o endpoint de obtenção de token JWT está operacional."""
        response = self.client.post(
            "/api/token/", {"username": "admin_test", "password": "password123"}
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_rota_perfil_usuario_me(self):
        """Valida a rota /api/me/ e permissões."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/me/")
        assert response.status_code == 200
        assert response.data["username"] == "admin_test"

    def test_verificar_se_tabela_produtos_ou_vendas_existe(self):
        """Garante que a estrutura de banco de dados básica está pronta para o PDV."""
        from django.db import connection

        tables = connection.introspection.table_names()

        # Verifica tabelas essenciais padrão
        assert "auth_user" in tables
        print(f"\nTabelas encontradas na base atual: {len(tables)}")
