from adrf import serializers
from adrf.serializers import ListSerializer
from adrf.serializers import ModelSerializer
from adrf.serializers import Serializer

from at_krl_editor.apps.knowledge_base.models import KEvent
from at_krl_editor.apps.knowledge_base.models import KInterval
from at_krl_editor.apps.knowledge_base.models import KnowledgeBase
from at_krl_editor.apps.knowledge_base.models import KObject
from at_krl_editor.apps.knowledge_base.models import KObjectAttribute
from at_krl_editor.apps.knowledge_base.models import KRule
from at_krl_editor.apps.knowledge_base.models import KRuleElseInstruction
from at_krl_editor.apps.knowledge_base.models import KRuleInstruction
from at_krl_editor.apps.knowledge_base.models import KType
from at_krl_editor.apps.knowledge_base.models import KTypeValue


class KnowledgeBaseSerializer(ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = "__all__"


class UploadKBSerializer(Serializer):
    file = serializers.FileField(write_only=True)
    success = serializers.BooleanField(default=True, read_only=True)
    knowledge_base = KnowledgeBaseSerializer(read_only=True)


class KTypeValueSerializer(ModelSerializer):
    class Meta:
        model = KTypeValue
        exclude = ("type",)


class KTypeSetValueInstanceSerializer(ModelSerializer):
    class Meta:
        model = KTypeValue
        exclude = ("type",)
        read_only_fields = ("id",)


class KTypeSetValuesSerializer(ListSerializer):
    child = KTypeSetValueInstanceSerializer()


class KTypeSerializer(ModelSerializer):
    kt_values = KTypeValueSerializer(many=True, required=False)

    async def acreate(self, validated_data):
        kt_values = validated_data.pop("kt_values", None)
        instance = await super().acreate(validated_data)
        await self.update_values(instance, kt_values)
        return instance

    async def aupdate(self, instance, validated_data):
        kt_values = validated_data.pop("kt_values", None)
        instance = await super().aupdate(instance, validated_data)
        await self.update_values(instance, kt_values)
        return instance

    async def update_values(self, instance: KType, kt_values):
        if kt_values is not None:
            serializer = KTypeSetValuesSerializer(data=kt_values)
            serializer.is_valid(raise_exception=True)
            await instance.kt_values.all().adelete()
            await serializer.asave(type=instance)

    class Meta:
        model = KType
        fields = "__all__"
        read_only_fields = ("knowledge_base",)


class KObjectAttributeSerializer(ModelSerializer):
    class Meta:
        model = KObjectAttribute
        exclude = ("object",)


class KObjectSetAttributeInstanceSerializer(ModelSerializer):
    class Meta:
        model = KObjectAttribute
        exclude = ("object",)
        read_only_fields = ("id",)


class KObjectSetAttributesSerializer(ListSerializer):
    child = KObjectSetAttributeInstanceSerializer()


class KObjectSerializer(ModelSerializer):
    ko_attributes = KObjectAttributeSerializer(many=True, required=False)

    class Meta:
        model = KObject
        fields = "__all__"
        read_only_fields = ("knowledge_base",)

    async def acreate(self, validated_data):
        ko_attributes = validated_data.pop("ko_attributes", None)
        instance = await super().acreate(validated_data)
        await self.update_attributes(instance, ko_attributes)
        return instance

    async def aupdate(self, instance, validated_data):
        ko_attributes = validated_data.pop("ko_attributes", None)
        instance = await super().aupdate(instance, validated_data)
        await self.update_attributes(instance, ko_attributes)
        return instance

    async def update_attributes(self, instance: KObject, ko_attributes):
        if ko_attributes is not None:
            for attr in ko_attributes:
                if isinstance(attr.get("type"), KType):
                    attr["type"] = attr.get("type").pk
            serializer = KObjectSetAttributesSerializer(data=ko_attributes)
            await serializer.ais_valid(raise_exception=True)
            await instance.ko_attributes.all().adelete()
            await serializer.asave(object=instance)


class KEventSerializer(ModelSerializer):
    class Meta:
        model = KEvent
        fields = "__all__"
        read_only_fields = ("knowledge_base",)


class KIntervalSerializer(ModelSerializer):
    class Meta:
        model = KInterval
        fields = "__all__"
        read_only_fields = ("knowledge_base",)


class KRuleInstructionSerializer(ModelSerializer):
    class Meta:
        model = KRuleInstruction
        exclude = ("rule",)


class KRuleSetInstructionInstanceSerializer(ModelSerializer):
    class Meta:
        model = KRuleInstruction
        exclude = ("rule",)
        read_only_fields = ("id",)


class KRuleSetInstructionsSerializer(ListSerializer):
    child = KRuleSetInstructionInstanceSerializer()


class KRuleElseInstructionSerializer(ModelSerializer):
    class Meta:
        model = KRuleElseInstruction
        exclude = ("rule",)


class KRuleSetElseInstructionInstanceSerializer(ModelSerializer):
    class Meta:
        model = KRuleElseInstruction
        exclude = ("rule",)
        read_only_fields = ("id",)


class KRuleSetElseInstructionsSerializer(ListSerializer):
    child = KRuleSetElseInstructionInstanceSerializer()


class KRuleSerializer(ModelSerializer):
    kr_instructions = KRuleInstructionSerializer(many=True, required=False)
    kr_else_instructions = KRuleElseInstructionSerializer(many=True, required=False)

    class Meta:
        model = KRule
        fields = "__all__"
        read_only_fields = ("knowledge_base",)

    async def acreate(self, validated_data):
        kr_instructions = validated_data.pop("kr_instructions", None)
        kr_else_instructions = validated_data.pop("kr_else_instructions", None)
        instance = await super().acreate(validated_data)
        await self.update_all_instrictions(instance, kr_instructions, kr_else_instructions)
        return instance

    async def aupdate(self, instance, validated_data):
        kr_instructions = validated_data.pop("kr_instructions", None)
        kr_else_instructions = validated_data.pop("kr_else_instructions", None)
        instance = await super().aupdate(instance, validated_data)
        await self.update_all_instrictions(instance, kr_instructions, kr_else_instructions)
        return instance

    async def update_all_instrictions(self, instance: KRule, kr_instructions, kr_else_instructions):
        await self.update_instructions(instance, kr_instructions)
        await self.update_else_instructions(instance, kr_else_instructions)

    async def update_instructions(self, instance: KRule, kr_instructions):
        if kr_instructions is not None:
            serializer = KRuleSetInstructionsSerializer(data=kr_instructions)
            await serializer.ais_valid(raise_exception=True)
            await instance.kr_instructions.all().adelete()
            await serializer.asave(rule=instance)

    async def update_else_instructions(self, instance: KRule, kr_else_instructions):
        if kr_else_instructions is not None:
            serializer = KRuleSetElseInstructionsSerializer(data=kr_else_instructions)
            serializer.is_valid(raise_exception=True)
            await instance.kr_else_instructions.all().adelete()
            await serializer.asave(rule=instance)


class KRuleUpdateConditionAndInstructionsSerializer(ModelSerializer):
    kr_instructions = KRuleInstructionSerializer(many=True)
    kr_else_instructions = KRuleElseInstructionSerializer(many=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = KRule
        fields = "id", "kr_instructions", "kr_else_instructions", "condition"


class KRLSerializer(Serializer):
    krl = serializers.CharField(read_only=True)
