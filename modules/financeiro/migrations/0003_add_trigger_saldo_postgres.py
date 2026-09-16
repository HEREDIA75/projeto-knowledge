from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("financeiro", "0002_contabancaria_transacaofinanceira_conta"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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

            DROP TRIGGER IF EXISTS trigger_atualizar_saldo ON financeiro_transacao;

            CREATE TRIGGER trigger_atualizar_saldo
            AFTER INSERT OR UPDATE ON financeiro_transacao
            FOR EACH ROW
            EXECUTE FUNCTION atualizar_saldo_conta();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trigger_atualizar_saldo ON financeiro_transacao;
            DROP FUNCTION IF EXISTS atualizar_saldo_conta();
            """,
        )
    ]
