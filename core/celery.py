import os
from celery import Celery

# Define as configurações padrão do Django para o programa Celery.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Carrega as configurações do Django usando o prefixo CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Procura tarefas assíncronas em todos os apps instalados (tasks.py)
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
