import io
import json
from xml.etree.ElementTree import tostring

from django.http import FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
    def upload(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        file_type = file.name.split(".")[-1]
        if not file.name.endswith(".kbs") and not file.name.endswith(".xml") and not file.name.endswith(".json"):
            raise exceptions.ValidationError(f'File type ".{file_type}" is not supported')
        content = file.open("r").read().decode()
        instance = models.KnowledgeBase.objects.create(
            name=file.name[: -(len(file_type) + 1)], status=models.KnowledgeBase.StatusChoices.LOADING
        )
        if file.name.endswith(".kbs"):
            tasks.kb_from_krl.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".xml"):
            tasks.kb_from_xml.delay(pk=instance.pk, content=content)
        elif file.name.endswith(".json"):
            tasks.kb_from_json.delay(pk=instance.pk, content=content)
        kb_serializer = serializers.KnowledgeBaseSerializer(instance)
        return Response({"success": True, "knowledge_base": kb_serializer.data})

    @action(
        methods=["POST"], detail=True, serializer_class=serializers.UploadKBSerializer, parser_classes=[MultiPartParser]
    )
    def add_upload(self, request, *args, **kwargs):
        instance: models.KnowledgeBase = self.get_object()
        instance.status = models.KnowledgeBase.StatusChoices.LOADING
        instance.save()
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
        return Response({"success": True, "knowledge_base": kb_serializer.data})

    @action(methods=["GET"], detail=True, serializer_class=serializers.KRLSerializer)
    def krl(self, request, *args, **kwargs):
        instance = self.get_object()
        kb = KBService.convert_kb(instance)
        return Response({"krl": kb.krl})

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    def download_krl(self, request, *args, **kwargs):
        instance = self.get_object()
        kb = KBService.convert_kb(instance)
        buffer = io.BytesIO(kb.krl.encode())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".kbs")

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    def download_xml(self, request, *args, **kwargs):
        instance = self.get_object()
        kb = KBService.convert_kb(instance)
        buffer = io.BytesIO(tostring(kb.get_xml(), encoding="UTF-8"))
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".xml")

    @action(methods=["GET"], detail=True, serializer_class=serializers.serializers.Serializer)
    def download_json(self, request, *args, **kwargs):
        instance = self.get_object()
        kb = KBService.convert_kb(instance)
        buffer = io.BytesIO(json.dumps(kb.__dict__(), ensure_ascii=False).encode())
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=instance.name + ".json")


class KBRelatedMixin:
    def get_queryset(self):
        return self.queryset.filter(knowledge_base=self.knowledge_base)

    @property
    def knowledge_base(self):
        return models.KnowledgeBase.objects.get(id=self.kwargs["knowledge_base_pk"])

    def perform_create(self, serializer):
        return serializer.save(knowledge_base=self.knowledge_base)

    @action(methods=["GET"], detail=True)
    def duplicate(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data.pop("id", None)
        data["kb_id"] = self.get_free_name(instance)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_instance = self.perform_create(serializer)
        self.duplicate_extras(instance, new_instance)
        serializer = self.get_serializer(new_instance)
        return Response(serializer.data)

    def get_free_name(self, instance):
        model_class = instance.__class__
        counter = 1
        new_name = f"КОПИЯ_{instance.kb_id}"
        search_name = new_name
        others = model_class.objects.exclude(pk=instance.pk).filter(
            knowledge_base=self.knowledge_base, kb_id=search_name
        )
        while others.count():
            search_name = f"{new_name}_{counter}"
            counter += 1
            others = model_class.objects.exclude(pk=instance.pk).filter(
                knowledge_base=self.knowledge_base, kb_id=search_name
            )

        new_name = search_name
        return new_name

    def duplicate_extras(self, instance, new_instance):
        pass

    @action(methods=["GET"], detail=True, serializer_class=serializers.KRLSerializer)
    def krl(self, *args, **kwargs):
        instance = self.get_object()
        entity = KBService.convert(instance)
        return Response(data={"krl": entity.krl})


class KTypeViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KType.objects.all()
    serializer_class = serializers.KTypeSerializer

    def perform_update(self, serializer: serializers.KTypeSerializer):
        instance: models.KType = serializer.instance
        validated_data = serializer.validated_data
        if validated_data.get("meta", instance.meta) != instance.meta:
            instance.kt_values.all().delete()
        super().perform_update(serializer)

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KTypeSetValuesSerializer)
    def set_values(self, request, *args, **kwargs):
        instance: models.KType = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.kt_values.all().delete()
        serializer.save(type=instance)
        return Response(data=serializer.data)

    def duplicate_extras(self, instance, new_instance):
        for value in instance.kt_values.all():
            models.KTypeValue.objects.create(data=value.data, type=new_instance)
        return new_instance


class KTypeValueViewSet(ModelViewSet):
    queryset = models.KTypeValue.objects.all()
    serializer_class = serializers.KTypeValueSerializer

    def get_queryset(self):
        return self.queryset.filter(type=self.type)

    @property
    def type(self):
        return models.KType.objects.get(id=self.kwargs["k_type_pk"])

    def perform_create(self, serializer):
        return serializer.save(type=self.type)


class KObjectViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KObject.objects.all()
    serializer_class = serializers.KObjectSerializer

    def duplicate_extras(self, instance, new_instance):
        for attr in instance.ko_attributes.all():
            models.KObjectAttribute.objects.create(
                object=new_instance,
                kb_id=attr.kb_id,
                type=attr.type,
                comment=attr.comment,
            )

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KObjectSetAttributesSerializer)
    def set_attributes(self, request, *args, **kwargs):
        instance: models.KObject = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.ko_attributes.all().delete()
        serializer.save(object=instance)
        return Response(data=serializer.data)


class KObjectAttributeViewSet(ModelViewSet):
    queryset = models.KObjectAttribute.objects.all()
    serializer_class = serializers.KObjectAttributeSerializer

    def get_queryset(self):
        return self.queryset.filter(object=self.object)

    @property
    def object(self):
        return models.KObject.objects.get(id=self.kwargs["k_object_pk"])

    def perform_create(self, serializer):
        return serializer.save(object=self.object)


class KEventViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KEvent.objects.all()
    serializer_class = serializers.KEventSerializer


class KIntervalViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KInterval.objects.all()
    serializer_class = serializers.KIntervalSerializer


class KRuleViewSet(KBRelatedMixin, ModelViewSet):
    queryset = models.KRule.objects.all()
    serializer_class = serializers.KRuleSerializer

    def duplicate_extras(self, instance, new_instance):
        for instr in instance.kr_instructions.all():
            models.KRuleInstruction.objects.create(rule=new_instance, data=instr.data)
        for else_instr in instance.kr_else_instructions.all():
            models.KRuleElseInstruction.objects.create(rule=new_instance, data=else_instr.data)
        return new_instance

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KRuleSetInstructionsSerializer)
    def set_instructions(self, request, *args, **kwargs):
        instance: models.KRule = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.kr_instructions.all().delete()
        serializer.save(rule=instance)
        return Response(data=serializer.data)

    @action(methods=["PUT"], detail=True, serializer_class=serializers.KRuleSetElseInstructionsSerializer)
    def set_else_instructions(self, request, *args, **kwargs):
        instance: models.KRule = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.kr_else_instructions.all().delete()
        serializer.save(rule=instance)
        return Response(data=serializer.data)

    @action(
        methods=["PUT", "PATCH"],
        detail=True,
        serializer_class=serializers.KRuleUpdateConditionAndInstructionsSerializer,
    )
    def update_condition_and_instructions(self, request, *args, **kwargs):
        instance: models.KRule = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.update_rule_data(instance, serializer)
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data)

    def update_rule_data(
        self, rule: models.KRule, serializer: serializers.KRuleUpdateConditionAndInstructionsSerializer
    ):
        rule.condition = serializer.validated_data.pop("condition", rule.condition)
        rule.save()
        rule.kr_instructions.all().delete()
        rule.kr_else_instructions.all().delete()
        for instr_data in serializer.validated_data.get("kr_instructions", []):
            models.KRuleInstruction.objects.create(rule=rule, **instr_data)
        for else_instr_data in serializer.validated_data.get("kr_else_instructions", []):
            models.KRuleElseInstruction.objects.create(rule=rule, **else_instr_data)
        return rule


class KRuleInstructionViewSet(ModelViewSet):
    queryset = models.KRuleInstruction.objects.all()
    serializer_class = serializers.KRuleInstructionSerializer

    def get_queryset(self):
        return self.queryset.filter(rule=self.rule)

    @property
    def rule(self):
        return models.KRule.objects.get(id=self.kwargs["k_rule_pk"])

    def perform_create(self, serializer):
        return serializer.save(rule=self.rule)


class KRuleElseInstructionViewSet(ModelViewSet):
    queryset = models.KRuleElseInstruction.objects.all()
    serializer_class = serializers.KRuleElseInstructionSerializer

    def get_queryset(self):
        return self.queryset.filter(rule=self.rule)

    @property
    def rule(self):
        return models.KRule.objects.get(id=self.kwargs["k_rule_pk"])

    def perform_create(self, serializer):
        return serializer.save(rule=self.rule)
