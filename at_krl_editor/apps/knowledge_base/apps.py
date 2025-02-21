from django.apps import AppConfig


class KnowledgeBaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "at_krl_editor.apps.knowledge_base"
    label = "knowledge_base"
    verbose_name = "Базы знаний"
