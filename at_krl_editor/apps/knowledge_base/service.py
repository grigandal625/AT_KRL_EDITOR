import json
from xml.etree.ElementTree import fromstring

from at_krl.core.kb_class import KBClass
from at_krl.core.kb_class import PropertyDefinition
from at_krl.core.kb_class import TypeOrClassReference
from at_krl.core.kb_entity import KBEntity
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_type import KBFuzzyType
from at_krl.core.kb_type import KBNumericType
from at_krl.core.kb_type import KBSymbolicType
from at_krl.core.kb_type import KBType
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from at_krl.models.kb_class import KBClassModel
from at_krl.models.kb_entity import KBRootModel
from at_krl.models.kb_rule import KBRuleModel
from at_krl.models.kb_type import KBFuzzyTypeModel
from at_krl.models.kb_type import KBNumericTypeModel
from at_krl.models.kb_type import KBSymbolicTypeModel
from at_krl.models.temporal.allen_event import KBEventModel
from at_krl.models.temporal.allen_interval import KBIntervalModel
from at_krl.utils.context import Context

from at_krl_editor.apps.knowledge_base import models
from at_krl_editor.apps.knowledge_base.utils import service


class KBTypeRootModel(KBRootModel[KBFuzzyTypeModel | KBNumericTypeModel | KBSymbolicTypeModel]):
    def to_internal(self, context):
        return self.root.to_internal(context)


class KBService:
    MODEL_CONVERTOR_CLASS_MAPPLING = {
        models.KType: (service.KTypeConvertSerializer, KBType, KBTypeRootModel),
        models.KObject: (service.KObjectConvertSerializer, KBClass, KBClassModel),
        models.KEvent: (service.KEventConvertSerializer, KBEvent, KBEventModel),
        models.KInterval: (service.KIntervalConvertSerializer, KBInterval, KBIntervalModel),
        models.KRule: (service.KRuleConvertSerializer, KBRule, KBRuleModel),
    }

    @staticmethod
    async def convert(t) -> KBEntity:
        serializer_class, _, kb_entity_model = KBService.MODEL_CONVERTOR_CLASS_MAPPLING[t.__class__]
        serializer = serializer_class(t)
        data = await serializer.adata
        # data = json.loads(json.dumps(data))
        model = kb_entity_model(**data)
        context = Context(name="convert")
        kb_entity = model.to_internal(context)
        return kb_entity

    @staticmethod
    async def convert_kb(kb: models.KnowledgeBase) -> KnowledgeBase:
        result = KnowledgeBase()
        async for t in kb.k_types.all():
            result.types.append(await KBService.convert(t))
        async for o in kb.k_objects.all():
            kb_class: KBClass = await KBService.convert(o)
            object_id = kb_class.id
            class_id = result.get_free_class_id(object_id)
            kb_class.id = class_id
            result.classes.objects.append(kb_class)
            result.world.properties.append(
                PropertyDefinition(id=object_id, desc=kb_class.desc, type=TypeOrClassReference(id=kb_class.id))
            )
        async for i in kb.k_intervals.all():
            result.classes.intervals.append(await KBService.convert(i))
        async for e in kb.k_events.all():
            result.classes.events.append(await KBService.convert(e))
        async for r in kb.k_rules.all():
            result.add_rule(await KBService.convert(r))
        return result

    @staticmethod
    def to_model(
        t: KBEntity, kb: models.KnowledgeBase
    ) -> models.KType | models.KObject | models.KEvent | models.KInterval | models.KRule:
        if isinstance(t, KBType):
            return KBService.type_to_model(t, kb)
        elif isinstance(t, KBEvent):
            return KBService.event_to_model(t, kb)
        elif isinstance(t, KBInterval):
            return KBService.interval_to_model(t, kb)
        elif isinstance(t, KBClass):
            return KBService.object_to_model(t, kb)
        elif isinstance(t, KBRule):
            return KBService.rule_to_model(t, kb)

    @staticmethod
    def type_to_model(t: KBType, kb: models.KnowledgeBase) -> models.KType:
        meta_mapping = {
            KBNumericType.meta: models.KType.MetaTypeChoices.NUMBER,
            KBSymbolicType.meta: models.KType.MetaTypeChoices.STRING,
            KBFuzzyType.meta: models.KType.MetaTypeChoices.FUZZY,
        }
        create_kwargs = {"knowledge_base": kb, "kb_id": t.id, "meta": meta_mapping[t.meta], "comment": t.desc}
        result = models.KType.objects.create(**create_kwargs)
        if isinstance(t, KBNumericType):
            models.KTypeValue.objects.create(type=result, data=t.from_)
            models.KTypeValue.objects.create(type=result, data=t.to_)
        elif isinstance(t, KBSymbolicType):
            for v in t.values:
                models.KTypeValue.objects.create(type=result, data=v)
        elif isinstance(t, KBFuzzyType):
            for mf in t.membership_functions:
                models.KTypeValue.objects.create(type=result, data=mf.to_representation())
        return result

    @staticmethod
    def object_to_model(t: KBClass, kb: models.KnowledgeBase) -> models.KObject:
        result = models.KObject.objects.create(kb_id=t.id, knowledge_base=kb, group=t.group, comment=t.desc)
        for prop in t.properties:
            attr_type = kb.k_types.filter(kb_id=prop.type.id).first()
            models.KObjectAttribute.objects.create(kb_id=prop.id, object=result, type=attr_type, comment=prop.desc)
        return result

    @staticmethod
    def event_to_model(t: KBEvent, kb: models.KnowledgeBase) -> models.KEvent:
        return models.KEvent.objects.create(
            knowledge_base=kb, kb_id=t.id, occurance_condition=t.occurance_condition.to_representation(), comment=t.desc
        )

    @staticmethod
    def interval_to_model(t: KBInterval, kb: models.KnowledgeBase) -> models.KInterval:
        return models.KInterval.objects.create(
            knowledge_base=kb,
            kb_id=t.id,
            open=t.open.to_representation(),
            close=t.close.to_representation(),
            comment=t.desc,
        )

    @staticmethod
    def rule_to_model(t: KBRule, kb: models.KnowledgeBase) -> models.KRule:
        result = models.KRule.objects.create(
            knowledge_base=kb,
            kb_id=t.id,
            condition=t.condition.to_representation(),
            comment=t.desc,
        )

        for instr in t.instructions:
            models.KRuleInstruction.objects.create(rule=result, data=instr.to_representation())
        if t.else_instructions:
            for else_instr in t.else_instructions:
                models.KRuleElseInstruction.objects.create(rule=result, data=else_instr.__dict__())
        return result

    @staticmethod
    def knowledge_base_to_model(
        data_kb: KnowledgeBase, kb: models.KnowledgeBase = None, file_name: str = None
    ) -> models.KnowledgeBase:
        kb = kb or models.KnowledgeBase.objects.create(name=file_name)
        for t in data_kb.types:
            KBService.type_to_model(t, kb)
        for property in data_kb.world.properties:
            object_id = property.id
            class_id = property.type.id

            cls = data_kb.get_object_by_id(class_id)
            cls.id = object_id
            KBService.object_to_model(cls, kb)

            cls.id = class_id
        for i in data_kb.classes.intervals:
            KBService.interval_to_model(i, kb)
        for e in data_kb.classes.events:
            KBService.event_to_model(e, kb)
        for r in data_kb.world.rules:
            KBService.rule_to_model(r, kb)
        return kb

    @staticmethod
    def kb_from_krl(krl_text: str) -> KnowledgeBase:
        return KnowledgeBase.from_krl(krl_text)

    @staticmethod
    def kb_from_xml(xml_text: str) -> KnowledgeBase:
        kb_xml = fromstring(xml_text)
        return KnowledgeBase.from_xml(kb_xml)

    @staticmethod
    def kb_from_json(json_text: str) -> KnowledgeBase:
        kb_dict = json.loads(json_text)
        return KnowledgeBase.from_json(kb_dict)
