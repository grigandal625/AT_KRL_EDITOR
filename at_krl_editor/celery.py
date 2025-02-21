import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "at_krl_editor.base_server.settings")
)

app = Celery("at_krl_editor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
