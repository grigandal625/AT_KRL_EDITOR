import io
import json
from xml.etree.ElementTree import tostring

from adrf.viewsets import ModelViewSet
from async_property import async_property
from django.http import FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from at_krl_editor.apps.knowledge_base import models
from at_krl_editor.apps.knowledge_base import serializers
from at_krl_editor.apps.knowledge_base import tasks
from at_krl_editor.apps.knowledge_base.service import KBService


class KnowledgeBaseViewSet(ModelViewSet):
    queryset = models.KnowledgeBase.objects.all()
    serializer_class = serializers.KnowledgeBaseSerializer

    @method_decorator(csrf_exempt)
    def perform_authentication(self, request):
        try:
            request.user
        except Exception as e:
            raise e

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=serializers.UploadKBSerializer,
        parser_classes=[MultiPartParser],
    )
    async def upload(self, request, *args, **kwargs):
        serializer: serializers.UploadKBSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        file_type = file.name.split(".")[-1]
        if not file.name.endswith(".kbs") and not file.name.endswith(".xml") and not file.name.endswith(".json"):
            raise exceptions.ValidationError(f'File type ".{file_type}" is not supported')
        content = file.open("r").read().decode()
        instance = await models.KnowledgeBase.objects.acreate(
            name=file.name[: -(len(file_type) + 1)], status=models.KnowledgeBase.StatusChoices.LOADING
        )
        if file.name.endswith(".kbs"):
            tasks.kb_from_krl.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".xml"):
            tasks.kb_from_xml.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".json"):
            tasks.kb_from_json.delay(pk=instance.pk, content=content)
        kb_serializer = serializers.KnowledgeBaseSerializer(instance)
        data = await kb_serializer.adata
        return Response({"success": True, "knowledge_base": data})

    @action(
        methods=["POST"], detail=True, serializer_class=serializers.UploadKBSerializer, parser_classes=[MultiPartParser]
    )
    async def add_upload(self, request, *args, **kwargs):
        instance: models.KnowledgeBase = await self.aget_object()
        instance.status = models.KnowledgeBase.StatusChoices.LOADING
        await instance.asave()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        file_type = file.name.split(".")[-1]
        if not file.name.endswith(".kbs") and not file.name.endswith(".xml") and not file.name.endswith(".json"):
            raise exceptions.ValidationError(f'File type ".{file_type}" is not supported')

        content = file.open("r").read().decode()
        if file.name.endswith(".kbs"):
            tasks.kb_from_krl.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".xml"):
            tasks.kb_from_xml.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".json"):
            tasks.kb_from_json.delay(pk=instance.pk, content=content)
        kb_serializer = serializers.KnowledgeBaseSerializer(instance)
        data = await kb_serializer.adata
        return Response({"success": True, "knowledge_base": data})

    @action(methods=["GET"], detail=True, serializer_class=serializers.KRLSerializer)
    async def krl(self, request, *args, **kwargs):
        instance = await self.aget_object()
        kb = await KBService.convert_kb(instance)
        return Response({"krl": kb.krl})

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    async def download_krl(self, request, *args, **kwargs):
        instance = await self.aget_object()
        kb = await KBService.convert_kb(instance)
        buffer = io.BytesIO(kb.krl.encode())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".kbs")

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    async def download_xml(self, request, *args, **kwargs):
        instance = await self.aget_object()
        kb = await KBService.convert_kb(instance)
        buffer = io.BytesIO(tostring(kb.get_xml(), encoding="UTF-8"))
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".xml")

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    async def download_json(self, request, *args, **kwargs):
        instance = await self.aget_object()
        kb = await KBService.convert_kb(instance)
        buffer = io.BytesIO(json.dumps(kb.__dict__(), ensure_ascii=False).encode())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".json")


class KBRelatedMixin:
    def get_queryset(self):
        return self.queryset.filter(knowledge_base_id=self.kwargs["knowledge_base_pk"])

    @async_property
    async def knowledge_base(self):
        return await models.KnowledgeBase.objects.aget(id=self.kwargs["knowledge_base_pk"])

    async def perform_acreate(self, serializer):
        kb = await self.knowledge_base
        return await serializer.asave(knowledge_base=kb)

    @action(methods=["GET"], detail=True)
    async def duplicate(self: ModelViewSet, request, *args, **kwargs):
        instance = await self.aget_object()
        serializer = self.get_serializer(instance)
        data = await serializer.adata
        data.pop("id", None)
        data["kb_id"] = await self.get_free_name(instance)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_instance = await self.perform_acreate(serializer)
        await self.duplicate_extras(instance, new_instance)
        serializer = self.get_serializer(new_instance)
        data = await serializer.adata
        return Response(data)

    async def get_free_name(self, instance):
        model_class = instance.__class__
        counter = 1
        new_name = f"КОПИЯ_{instance.kb_id}"
        search_name = new_name
        others = model_class.objects.exclude(pk=instance.pk).filter(
            knowledge_base=self.knowledge_base, kb_id=search_name
        )
        while await others.acount():
            search_name = f"{new_name}_{counter}"
            counter += 1
            others = model_class.objects.exclude(pk=instance.pk).filter(
                knowledge_base=self.knowledge_base, kb_id=search_name
            )

        new_name = search_name
        return new_name

    async def duplicate_extras(self, instance, new_instance):
        pass

    @action(methods=["GET"], detail=True, serializer_class=serializers.KRLSerializer)
    async def krl(self: ModelViewSet, *args, **kwargs):
        instance = await self.aget_object()
        entity = await KBService.convert(instance)
        return Response(data={"krl": entity.krl})


class KTypeViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KType.objects.all()
    serializer_class = serializers.KTypeSerializer

    async def perform_aupdate(self, serializer: serializers.KTypeSerializer):
        instance: models.KType = serializer.instance
        validated_data = serializer.validated_data
        if validated_data.get("meta", instance.meta) != instance.meta:
            await instance.kt_values.all().adelete()
        await super().perform_aupdate(serializer)

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KTypeSetValuesSerializer)
    async def set_values(self, request, *args, **kwargs):
        instance: models.KType = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        await instance.kt_values.all().adelete()
        await serializer.asave(type=instance)
        return Response(data=serializer.data)

    async def duplicate_extras(self, instance, new_instance):
        async for value in instance.kt_values.all():
            await models.KTypeValue.objects.acreate(data=value.data, type=new_instance)
        return new_instance


class KTypeValueViewSet(ModelViewSet):
    queryset = models.KTypeValue.objects.all()
    serializer_class = serializers.KTypeValueSerializer

    def get_queryset(self):
        return self.queryset.filter(type=self.type)

    @async_property
    async def type(self):
        return await models.KType.objects.aget(id=self.kwargs["k_type_pk"])

    async def perform_acreate(self, serializer):
        return serializer.asave(type=await self.type)


class KObjectViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KObject.objects.all()
    serializer_class = serializers.KObjectSerializer

    async def duplicate_extras(self, instance, new_instance):
        async for attr in instance.ko_attributes.all():
            await models.KObjectAttribute.objects.acreate(
                object=new_instance,
                kb_id=attr.kb_id,
                type=attr.type,
                comment=attr.comment,
            )

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KObjectSetAttributesSerializer)
    async def set_attributes(self, request, *args, **kwargs):
        instance: models.KObject = await self.aget_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        await instance.ko_attributes.all().adelete()
        await serializer.asave(object=instance)
        return Response(data=serializer.data)


class KObjectAttributeViewSet(ModelViewSet):
    queryset = models.KObjectAttribute.objects.all()
    serializer_class = serializers.KObjectAttributeSerializer

    def get_queryset(self):
        return self.queryset.filter(object_id=self.kwargs["k_object_pk"])

    @async_property
    async def object(self):
        return await models.KObject.objects.aget(id=self.kwargs["k_object_pk"])

    async def perform_acreate(self, serializer):
        obj = await self.object
        return await serializer.asave(object=obj)


class KEventViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KEvent.objects.all()
    serializer_class = serializers.KEventSerializer


class KIntervalViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KInterval.objects.all()
    serializer_class = serializers.KIntervalSerializer


class KRuleViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KRule.objects.all()
    serializer_class = serializers.KRuleSerializer

    async def duplicate_extras(self, instance, new_instance):
        async for instr in instance.kr_instructions.all():
            await models.KRuleInstruction.objects.acreate(rule=new_instance, data=instr.data)
        async for else_instr in instance.kr_else_instructions.all():
            await models.KRuleElseInstruction.objects.acreate(rule=new_instance, data=else_instr.data)
        return new_instance

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KRuleSetInstructionsSerializer)
    async def set_instructions(self, request, *args, **kwargs):
        instance: models.KRule = await self.aget_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        await instance.kr_instructions.all().adelete()
        await serializer.asave(rule=instance)
        return Response(data=serializer.data)

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KRuleSetElseInstructionsSerializer)
    async def set_else_instructions(self, request, *args, **kwargs):
        instance: models.KRule = await self.aget_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        await instance.kr_else_instructions.all().adelete()
        await serializer.asave(rule=instance)
        return Response(data=serializer.data)

    @action(
        methods=["PUT", "PATCH"],
        detail=True,
        serializer_class=serializers.KRuleUpdateConditionAndInstructionsSerializer,
    )
    async def update_condition_and_instructions(self, request, *args, **kwargs):
        instance: models.KRule = await self.aget_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = await self.update_rule_data(instance, serializer)
        serializer = self.get_serializer(instance)
        return Response(data=await serializer.adata)

    async def update_rule_data(
        self, rule: models.KRule, serializer: serializers.KRuleUpdateConditionAndInstructionsSerializer
    ):
        rule.condition = serializer.validated_data.pop("condition", rule.condition)
        await rule.asave()
        await rule.kr_instructions.all().adelete()
        await rule.kr_else_instructions.all().adelete()
        async for instr_data in serializer.validated_data.get("kr_instructions", []):
            await models.KRuleInstruction.objects.acreate(rule=rule, **instr_data)
        async for else_instr_data in serializer.validated_data.get("kr_else_instructions", []):
            await models.KRuleElseInstruction.objects.acreate(rule=rule, **else_instr_data)
        return rule


class KRuleInstructionViewSet(ModelViewSet):
    queryset = models.KRuleInstruction.objects.all()
    serializer_class = serializers.KRuleInstructionSerializer

    def get_queryset(self):
        return self.queryset.filter(rule_id=self.kwargs["k_rule_pk"])

    @async_property
    async def rule(self):
        return await models.KRule.objects.aget(id=self.kwargs["k_rule_pk"])

    async def perform_acreate(self, serializer):
        return await serializer.asave(rule=await self.rule)


class KRuleElseInstructionViewSet(ModelViewSet):
    queryset = models.KRuleElseInstruction.objects.all()
    serializer_class = serializers.KRuleElseInstructionSerializer

    def get_queryset(self):
        return self.queryset.filter(rule_id=self.kwargs["k_rule_pk"])

    @async_property
    async def rule(self):
        return await models.KRule.objects.aget(id=self.kwargs["k_rule_pk"])

    async def perform_acreate(self, serializer):
        return await serializer.asave(rule=await self.rule)
