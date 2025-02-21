from rest_framework import serializers

from at_krl_editor.apps.knowledge_base.models import KEvent
from at_krl_editor.apps.knowledge_base.models import KInterval
from at_krl_editor.apps.knowledge_base.models import KObject
from at_krl_editor.apps.knowledge_base.models import KObjectAttribute
from at_krl_editor.apps.knowledge_base.models import KRule
from at_krl_editor.apps.knowledge_base.models import KType
from at_krl_editor.apps.knowledge_base.utils.serializers import AttrAsIsRelatedField
from at_krl_editor.apps.knowledge_base.utils.serializers import AttrStringRelatedField
from at_krl_editor.apps.knowledge_base.utils.serializers import FMModelSerializer


class NumericTypeConvertSerializer(FMModelSerializer):
    field_name_map = {
        "_from": "from",
        "_to": "to",
    }

    id = serializers.CharField(source="kb_id")
    _from = serializers.FloatField(source="kt_values.first.data")
    _to = serializers.FloatField(source="kt_values.last.data")
    desc = serializers.CharField(source="comment")
    meta = serializers.SerializerMethodField()

    def get_meta(self, value):
        return "number"

    class Meta:
        model = KType
        fields = "id", "_from", "_to", "desc", "meta"


class SymbolicTypeConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    values = AttrStringRelatedField(many=True, source="kt_values", attr="data")
    desc = serializers.CharField(source="comment")
    meta = serializers.SerializerMethodField()

    def get_meta(self, value):
        return "string"

    class Meta:
        model = KType
        fields = "id", "values", "desc", "meta"


class FuzzyTypeConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    membership_functions = AttrAsIsRelatedField(many=True, source="kt_values", attr="data", read_only=True)
    desc = serializers.CharField(source="comment")
    meta = serializers.SerializerMethodField()

    def get_meta(self, value):
        return "fuzzy"

    class Meta:
        model = KType
        fields = "id", "membership_functions", "desc", "meta"


class KTypeConvertSerializer(NumericTypeConvertSerializer, SymbolicTypeConvertSerializer, FuzzyTypeConvertSerializer):
    id = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")

    def to_representation(self, instance: KType):
        if instance.meta == KType.MetaTypeChoices.NUMBER:
            return NumericTypeConvertSerializer(instance).to_representation(instance)
        elif instance.meta == KType.MetaTypeChoices.STRING:
            return SymbolicTypeConvertSerializer(instance).to_representation(instance)
        elif instance.meta == KType.MetaTypeChoices.FUZZY:
            return FuzzyTypeConvertSerializer(instance).to_representation(instance)

    class Meta:
        model = KType
        fields = "id", "desc"


class KObjectAttrConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    type = serializers.CharField(source="type.kb_id")
    desc = serializers.CharField(source="comment")
    source = serializers.SerializerMethodField()

    def get_source(self, value):
        return "asked"

    class Meta:
        model = KObjectAttribute
        fields = "id", "type", "desc", "source"


class KObjectConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    group = serializers.CharField()
    properties = KObjectAttrConvertSerializer(many=True, source="ko_attributes")

    class Meta:
        model = KObject
        fields = "id", "desc", "properties", "group"


class KEventConvertSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    Formula = serializers.JSONField(source="occurance_condition")

    class Meta:
        model = KEvent
        fields = "Name", "desc", "Formula"


class KIntervalConvertSerializer(serializers.ModelSerializer):
    Name = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    Open = serializers.JSONField(source="open")
    Close = serializers.JSONField(source="close")

    class Meta:
        model = KInterval
        fields = "Name", "desc", "Open", "Close"


class KRuleConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    instructions = AttrAsIsRelatedField(many=True, source="kr_instructions", attr="data", read_only=True)
    else_instructions = AttrAsIsRelatedField(many=True, source="kr_else_instructions", attr="data", read_only=True)

    class Meta:
        model = KRule
        fields = "id", "desc", "condition", "instructions", "else_instructions"
