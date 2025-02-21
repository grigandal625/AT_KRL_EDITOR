import traceback

from at_krl.core.knowledge_base import KnowledgeBase as CoreKB

from at_krl_editor.apps.knowledge_base.models import KnowledgeBase
from at_krl_editor.apps.knowledge_base.service import KBService
from at_krl_editor.celery import app


def prepare_kb(pk: int) -> KnowledgeBase:
    instance = KnowledgeBase.objects.get(pk=pk)
    instance.status = KnowledgeBase.StatusChoices.LOADING
    instance.save()
    return instance


def update_kb(kb: CoreKB, instance: KnowledgeBase, file_name: str = None):
    instance = KBService.knowledge_base_to_model(kb, instance, file_name=file_name)
    instance.status = KnowledgeBase.StatusChoices.OK
    instance.save()
    return instance


@app.task
def kb_from_krl(pk: int, content: str, file_name: str = None):
    instance = prepare_kb(pk)
    try:
        kb = KBService.kb_from_krl(content)
        instance = update_kb(kb, instance, file_name=file_name)
    except Exception:
        instance.status = KnowledgeBase.StatusChoices.ERROR
        instance.error = traceback.format_exc()
        instance.save()


@app.task
def kb_from_xml(pk: int, content: str, file_name: str = None):
    instance = prepare_kb(pk)
    try:
        kb = KBService.kb_from_xml(content)
        instance = update_kb(kb, instance, file_name=file_name)
    except Exception:
        instance.status = KnowledgeBase.StatusChoices.ERROR
        instance.error = traceback.format_exc()
        instance.save()


@app.task
def kb_from_json(pk: int, content: str, file_name: str = None):
    instance = prepare_kb(pk)
    try:
        kb = KBService.kb_from_json(content)
        instance = update_kb(kb, instance, file_name=file_name)
    except Exception:
        instance.status = KnowledgeBase.StatusChoices.ERROR
        instance.error = traceback.format_exc()
        instance.save()
