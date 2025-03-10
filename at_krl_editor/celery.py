import os

from celery import Celery

from at_krl_editor.utils.settings import get_django_settings_module

os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_django_settings_module())

app = Celery("at_krl_editor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
