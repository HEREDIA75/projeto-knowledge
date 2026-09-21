from django.db import migrations


def criar_trigger_postgres(apps, schema_editor):
    # Executa a Trigger e a Function APENAS se o banco for PostgreSQL
    if schema_editor.connection.vendor == "postgresql":
        sql = """
        CREATE OR REPLACE FUNCTION atualizar_saldo_conta()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (NEW.status = 'PAGO') THEN
                IF (NEW.tipo = 'RECEITA') THEN
                    UPDATE financeiro_contabancaria 
                    SET saldo_atual = saldo_atual + NEW.valor 
                    WHERE id = NEW.conta_id;
                ELSIF (NEW.tipo = 'DESPESA') THEN
                    UPDATE financeiro_contabancaria 
                    SET saldo_atual = saldo_atual - NEW.valor 
                    WHERE id = NEW.conta_id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trigger_atualizar_saldo ON financeiro_transacaofinanceira;

        CREATE TRIGGER trigger_atualizar_saldo
        AFTER INSERT OR UPDATE ON financeiro_transacaofinanceira
        FOR EACH ROW
        EXECUTE FUNCTION atualizar_saldo_conta();
        """
        schema_editor.execute(sql)


def remover_trigger_postgres(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        sql = """
        DROP TRIGGER IF EXISTS trigger_atualizar_saldo ON financeiro_transacaofinanceira;
        DROP FUNCTION IF EXISTS atualizar_saldo_conta();
        """
        schema_editor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ("financeiro", "0002_contabancaria_transacaofinanceira_conta"),
    ]

    operations = [
        migrations.RunPython(
            criar_trigger_postgres,
            reverse_code=remover_trigger_postgres,
        ),
    ]
