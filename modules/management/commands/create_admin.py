from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = "Cria um superusuario via variaveis de ambiente"

    def handle(self, *args, **options):
        User = get_user_model()
        username = config("ADMIN_USERNAME", default="admin")
        email = config("ADMIN_EMAIL", default="admin@example.com")
        password = config("ADMIN_PASSWORD", default="SenhaSegura123!")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!')
            )
        else:
            self.stdout.write(self.style.WARNING(f'Usuário "{username}" já existe.'))
