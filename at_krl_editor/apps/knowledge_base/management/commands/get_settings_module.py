import os

from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        return os.getenv("DJANGO_SETTINGS_MODULE")
