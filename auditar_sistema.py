# auditar_sistema.py
import os
import sys
import django

# 1. Configuração do ambiente Django
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "core.settings"
)  # <--- Ajuste para o nome do seu modulo de settings se necessário
django.setup()

from django.urls import get_resolver
from django.db import connection, models
from django.apps import apps


def listar_rotas():
    print("\n" + "=" * 50)
    print(" 1. MAPEAMENTO DE ROTAS & APIS (ENDPOINTS)")
    print("=" * 50)
    resolver = get_resolver()

    def extrair_urls(url_patterns, prefix=""):
        urls = []
        for pattern in url_patterns:
            if hasattr(pattern, "url_patterns"):
                urls.extend(
                    extrair_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                )
            else:
                urls.append(prefix + str(pattern.pattern))
        return urls

    rotas = extrair_urls(resolver.url_patterns)
    for rota in sorted(rotas):
        print(f" [URL] /{rota}")
    print(f" Total de rotas mapeadas: {len(rotas)}")


def listar_modelos_e_banco():
    print("\n" + "=" * 50)
    print(" 2. TABELAS, MODELS E ESTRUTURA DO BANCO DE DADOS")
    print("=" * 50)

    app_models = apps.get_models()
    print(f" Total de Models Registrados: {len(app_models)}\n")

    for model in app_models:
        meta = model._meta
        print(f"📌 Model: {model.__name__} (Tabela: '{meta.db_table}')")
        campos = [f.name for f in meta.get_fields()]
        print(f"   Fields: {', '.join(campos[:8])}{'...' if len(campos) > 8 else ''}")


def testar_triggers_functions_views():
    print("\n" + "=" * 50)
    print(" 3. DIAGNÓSTICO DB: FUNCTIONS, TRIGGERS E VIEWS")
    print("=" * 50)

    vendor = connection.vendor
    print(f" Motor do Banco de Dados: {vendor.upper()}")

    with connection.cursor() as cursor:
        if vendor == "postgresql":
            # Listar Triggers
            cursor.execute("""
                SELECT trigger_name, event_object_table 
                FROM information_schema.triggers 
                WHERE trigger_schema NOT IN ('pg_catalog', 'information_schema');
            """)
            triggers = cursor.fetchall()
            print(f"\n⚡ Triggers Encontradas ({len(triggers)}):")
            for t in triggers:
                print(f"   - {t[0]} na tabela '{t[1]}'")

            # Listar Functions/Procedures
            cursor.execute("""
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_schema = 'public';
            """)
            functions = cursor.fetchall()
            print(f"\n⚙️ Functions/Procedures ({len(functions)}):")
            for f in functions:
                print(f"   - {f[0]}()")

        elif vendor == "mysql":
            cursor.execute("SHOW TRIGGERS;")
            triggers = cursor.fetchall()
            print(f"\n⚡ Triggers Encontradas ({len(triggers)}):")
            for t in triggers:
                print(f"   - {t[0]} na tabela '{t[1]}'")

            cursor.execute("SHOW FUNCTION STATUS WHERE Db = DATABASE();")
            functions = cursor.fetchall()
            print(f"\n⚙️ Functions ({len(functions)}):")
            for f in functions:
                print(f"   - {f[1]}()")


def testar_queries_e_joins():
    print("\n" + "=" * 50)
    print(" 4. TESTE DE QUERIES COM JOIN & INTEGRIDADE")
    print("=" * 50)

    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        # Teste 1: Contagem basica (Seeders/Massa de dados)
        total_users = User.objects.count()
        print(f" Status de Usuários (Seeders/Users): {total_users} registrados.")

        # Teste 2: Exemplo de JOIN genérico (User -> Groups)
        users_with_groups = (
            User.objects.filter(groups__isnull=False).select_related().distinct()
        )
        print(
            f" Teste de Query com JOIN (Usuários com Grupos/Permissões): {users_with_groups.count()} encontrados."
        )
        print(" ✅ ORM Django & Joins operando normalmente.")

    except Exception as e:
        print(f" ❌ Erro ao executar queries de teste: {e}")


if __name__ == "__main__":
    print("🔍 INICIANDO AUDITORIA DE REQUISITOS TÉCNICOS DO ERP...")
    listar_rotas()
    listar_modelos_e_banco()
    testar_triggers_functions_views()
    testar_queries_e_joins()
    print("\n✅ DIAGNÓSTICO CONCLUÍDO COM SUCESSO!")
