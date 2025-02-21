from rest_framework import serializers

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


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = "__all__"


class UploadKBSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    success = serializers.BooleanField(default=True, read_only=True)
    knowledge_base = KnowledgeBaseSerializer(read_only=True)


class KTypeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = KTypeValue
        exclude = ("type",)


class KTypeSetValueInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = KTypeValue
        exclude = ("type",)
        read_only_fields = ("id",)


class KTypeSetValuesSerializer(serializers.ListSerializer):
    child = KTypeSetValueInstanceSerializer()


class KTypeSerializer(serializers.ModelSerializer):
    kt_values = KTypeValueSerializer(many=True, required=False)

    def create(self, validated_data):
        kt_values = validated_data.pop("kt_values", None)
        instance = super().create(validated_data)
        self.update_values(instance, kt_values)
        return instance

    def update(self, instance, validated_data):
        kt_values = validated_data.pop("kt_values", None)
        instance = super().update(instance, validated_data)
        self.update_values(instance, kt_values)
        return instance

    def update_values(self, instance: KType, kt_values):
        if kt_values is not None:
            serializer = KTypeSetValuesSerializer(data=kt_values)
            serializer.is_valid(raise_exception=True)
            instance.kt_values.all().delete()
            serializer.save(type=instance)

    class Meta:
        model = KType
        exclude = ("knowledge_base",)


class KObjectAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = KObjectAttribute
        exclude = ("object",)


class KObjectSetAttributeInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = KObjectAttribute
        exclude = ("object",)
        read_only_fields = ("id",)


class KObjectSetAttributesSerializer(serializers.ListSerializer):
    child = KObjectSetAttributeInstanceSerializer()


class KObjectSerializer(serializers.ModelSerializer):
    ko_attributes = KObjectAttributeSerializer(many=True, required=False)

    class Meta:
        model = KObject
        exclude = ("knowledge_base",)

    def create(self, validated_data):
        ko_attributes = validated_data.pop("ko_attributes", None)
        instance = super().create(validated_data)
        self.update_attributes(instance, ko_attributes)
        return instance

    def update(self, instance, validated_data):
        ko_attributes = validated_data.pop("ko_attributes", None)
        instance = super().update(instance, validated_data)
        self.update_attributes(instance, ko_attributes)
        return instance

    def update_attributes(self, instance: KObject, ko_attributes):
        if ko_attributes is not None:
            for attr in ko_attributes:
                if isinstance(attr.get("type"), KType):
                    attr["type"] = attr.get("type").pk
            serializer = KObjectSetAttributesSerializer(data=ko_attributes)
            serializer.is_valid(raise_exception=True)
            instance.ko_attributes.all().delete()
            serializer.save(object=instance)


class KEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = KEvent
        exclude = ("knowledge_base",)


class KIntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = KInterval
        exclude = ("knowledge_base",)


class KRuleInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRuleInstruction
        exclude = ("rule",)


class KRuleSetInstructionInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRuleInstruction
        exclude = ("rule",)
        read_only_fields = ("id",)


class KRuleSetInstructionsSerializer(serializers.ListSerializer):
    child = KRuleSetInstructionInstanceSerializer()


class KRuleElseInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRuleElseInstruction
        exclude = ("rule",)


class KRuleSetElseInstructionInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRuleElseInstruction
        exclude = ("rule",)
        read_only_fields = ("id",)


class KRuleSetElseInstructionsSerializer(serializers.ListSerializer):
    child = KRuleSetElseInstructionInstanceSerializer()


class KRuleSerializer(serializers.ModelSerializer):
    kr_instructions = KRuleInstructionSerializer(many=True, required=False)
    kr_else_instructions = KRuleElseInstructionSerializer(many=True, required=False)

    class Meta:
        model = KRule
        exclude = ("knowledge_base",)

    def create(self, validated_data):
        kr_instructions = validated_data.pop("kr_instructions", None)
        kr_else_instructions = validated_data.pop("kr_else_instructions", None)
        instance = super().create(validated_data)
        self.update_all_instrictions(instance, kr_instructions, kr_else_instructions)
        return instance

    def update(self, instance, validated_data):
        kr_instructions = validated_data.pop("kr_instructions", None)
        kr_else_instructions = validated_data.pop("kr_else_instructions", None)
        instance = super().update(instance, validated_data)
        self.update_all_instrictions(instance, kr_instructions, kr_else_instructions)
        return instance

    def update_all_instrictions(self, instance: KRule, kr_instructions, kr_else_instructions):
        self.update_instructions(instance, kr_instructions)
        self.update_else_instructions(instance, kr_else_instructions)

    def update_instructions(self, instance: KRule, kr_instructions):
        if kr_instructions is not None:
            serializer = KRuleSetInstructionsSerializer(data=kr_instructions)
            serializer.is_valid(raise_exception=True)
            instance.kr_instructions.all().delete()
            serializer.save(rule=instance)

    def update_else_instructions(self, instance: KRule, kr_else_instructions):
        if kr_else_instructions is not None:
            serializer = KRuleSetElseInstructionsSerializer(data=kr_else_instructions)
            serializer.is_valid(raise_exception=True)
            instance.kr_else_instructions.all().delete()
            serializer.save(rule=instance)


class KRuleUpdateConditionAndInstructionsSerializer(serializers.ModelSerializer):
    kr_instructions = KRuleInstructionSerializer(many=True)
    kr_else_instructions = KRuleElseInstructionSerializer(many=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = KRule
        fields = "id", "kr_instructions", "kr_else_instructions", "condition"


class KRLSerializer(serializers.Serializer):
    krl = serializers.CharField(read_only=True)
