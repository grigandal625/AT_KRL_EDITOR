from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import component_method
from typing import Union

from at_krl_editor.apps.knowledge_base.models import KEvent
from at_krl_editor.apps.knowledge_base.models import KInterval
from at_krl_editor.apps.knowledge_base.models import KnowledgeBase
from at_krl_editor.apps.knowledge_base.models import KObject
from at_krl_editor.apps.knowledge_base.models import KRule
from at_krl_editor.apps.knowledge_base.models import KType
from at_krl_editor.apps.knowledge_base.serializers import KEventSerializer
from at_krl_editor.apps.knowledge_base.serializers import KIntervalSerializer
from at_krl_editor.apps.knowledge_base.serializers import KnowledgeBaseSerializer
from at_krl_editor.apps.knowledge_base.serializers import KObjectSerializer
from at_krl_editor.apps.knowledge_base.serializers import KRuleSerializer
from at_krl_editor.apps.knowledge_base.serializers import KTypeSerializer
from at_krl_editor.apps.knowledge_base.service import KBService


class ATKRLEditor(ATComponent):
    @component_method
    async def get_knowledge_bases(self, **kwargs):
        bases = KnowledgeBase.objects.all()
        serializer = KnowledgeBaseSerializer(bases, many=True)
        return await serializer.adata

    @component_method
    async def get_knowledge_base(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        kb_model = await KnowledgeBase.objects.aget(pk=id)
        if kb_model.status != KnowledgeBase.StatusChoices.OK:
            raise ValueError(
                f"Kowledge base with id {id} has status "
                f"{KnowledgeBase.StatusChoices._value2member_map_[kb_model.status].name}"
            )
        if format == "db":
            serializer = KnowledgeBaseSerializer(kb_model)
            return await serializer.adata
        kb = await KBService.convert_kb(kb_model)
        if format == "at_krl":
            return kb.krl
        if format == "xml":
            return kb.xml_str
        return kb.to_representation()

    @component_method
    async def get_knowledge_base_types(self, id: Union[int, str], **kwargs) -> dict:
        id = int(id)
        types = await KType.objects.filter(knowledge_base_id=id)
        serializer = KTypeSerializer(types, many=True)
        return await serializer.adata

    @component_method
    async def get_knowledge_base_objects(self, id: Union[int, str], **kwargs) -> dict:
        id = int(id)
        objects = await KObject.objects.filter(knowledge_base_id=id)
        serializer = KObjectSerializer(objects, many=True)
        return await serializer.adata

    @component_method
    async def get_knowledge_base_events(self, id: Union[int, str], **kwargs) -> dict:
        id = int(id)
        events = await KEvent.objects.filter(knowledge_base_id=id)
        serializer = KEventSerializer(events, many=True)
        return await serializer.adata

    @component_method
    async def get_knowledge_base_intervals(self, id: Union[int, str], **kwargs) -> dict:
        intervals = await KInterval.objects.filter(knowledge_base_id=id)
        serializer = KIntervalSerializer(intervals, many=True)
        return await serializer.adata

    @component_method
    async def get_knowledge_base_rules(self, id: Union[int, str], **kwargs) -> dict:
        id = int(id)
        rules = await KRule.objects.filter(knowledge_base_id=id)
        serializer = KRuleSerializer(rules, many=True)
        return await serializer.adata

    @component_method
    async def get_type(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        type_model = await KType.objects.aget(pk=id)
        if format == "db":
            serializer = KTypeSerializer(type_model)
            return await serializer.adata
        kb_type = await KBService.convert(type_model)
        if format == "at_krl":
            return kb_type.krl
        if format == "xml":
            return kb_type.xml_str
        return kb_type.to_representation()

    @component_method
    async def get_object(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        object_model = await KObject.objects.aget(pk=id)
        if format == "db":
            serializer = KObjectSerializer(object_model)
            return await serializer.adata
        kb_object = await KBService.convert(object_model)
        if format == "at_krl":
            return kb_object.krl
        if format == "xml":
            return kb_object.xml_str
        return kb_object.to_representation()

    @component_method
    async def get_event(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        event_model = await KEvent.objects.aget(pk=id)
        if format == "db":
            serializer = KEventSerializer(event_model)
            return await serializer.adata
        kb_event = await KBService.convert(event_model)
        if format == "at_krl":
            return kb_event.krl
        if format == "xml":
            return kb_event.xml_str
        return kb_event.to_representation()

    @component_method
    async def get_interval(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        interval_model = await KInterval.objects.aget(pk=id)
        if format == "db":
            serializer = KIntervalSerializer(interval_model)
            return await serializer.adata
        kb_interval = await KBService.convert(interval_model)
        if format == "at_krl":
            return kb_interval.krl
        if format == "xml":
            return kb_interval.xml_str
        return kb_interval.to_representation()

    @component_method
    async def get_rule(self, id: Union[int, str], format: str = "json", **kwargs) -> dict | str:
        id = int(id)
        rule_model = await KRule.objects.aget(pk=id)
        if format == "db":
            serializer = KRuleSerializer(rule_model)
            return await serializer.adata
        kb_rule = await KBService.convert(rule_model)
        if format == "at_krl":
            return kb_rule.krl
        if format == "xml":
            return kb_rule.xml_str
        return kb_rule.to_representation()
