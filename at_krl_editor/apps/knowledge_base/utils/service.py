from adrf import fields
from adrf import serializers

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
        "from_": "from",
        "to_": "to",
    }

    id = serializers.CharField(source="kb_id")
    from_ = serializers.FloatField(source="kt_values.first.data")
    to_ = serializers.FloatField(source="kt_values.last.data")
    desc = serializers.CharField(source="comment")
    meta = fields.SerializerMethodField()
    tag = fields.SerializerMethodField()

    def get_meta(self, value):
        return "number"

    def get_tag(self, value):
        return "type"

    class Meta:
        model = KType
        fields = "id", "from_", "to_", "desc", "meta", "tag"


class SymbolicTypeConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    values = AttrStringRelatedField(many=True, source="kt_values", attr="data")
    desc = serializers.CharField(source="comment")
    meta = fields.SerializerMethodField()
    tag = fields.SerializerMethodField()

    def get_meta(self, value):
        return "string"

    def get_tag(self, value):
        return "type"

    class Meta:
        model = KType
        fields = "id", "values", "desc", "meta", "tag"


class FuzzyTypeConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    membership_functions = AttrAsIsRelatedField(many=True, source="kt_values", attr="data", read_only=True)
    desc = serializers.CharField(source="comment")
    meta = fields.SerializerMethodField()
    tag = fields.SerializerMethodField()

    def get_meta(self, value):
        return "fuzzy"

    def get_tag(self, value):
        return "type"

    class Meta:
        model = KType
        fields = "id", "membership_functions", "desc", "meta", "tag"


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

    async def ato_representation(self, instance: KType):
        if instance.meta == KType.MetaTypeChoices.NUMBER:
            return await NumericTypeConvertSerializer(instance).ato_representation(instance)
        elif instance.meta == KType.MetaTypeChoices.STRING:
            return await SymbolicTypeConvertSerializer(instance).ato_representation(instance)
        elif instance.meta == KType.MetaTypeChoices.FUZZY:
            return await FuzzyTypeConvertSerializer(instance).ato_representation(instance)

    class Meta:
        model = KType
        fields = "id", "desc", "tag"


class KObjectAttrConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    type = serializers.CharField(source="type.kb_id")
    desc = serializers.CharField(source="comment")
    source = fields.SerializerMethodField()
    tag = fields.SerializerMethodField()

    def get_tag(self, value):
        return "property"

    def get_source(self, value):
        return "asked"

    class Meta:
        model = KObjectAttribute
        fields = "id", "type", "desc", "source", "tag"


class KObjectConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    group = serializers.CharField()
    properties = KObjectAttrConvertSerializer(many=True, source="ko_attributes")
    tag = fields.SerializerMethodField()

    def get_tag(self, value):
        return "class"

    class Meta:
        model = KObject
        fields = "id", "desc", "properties", "group", "tag"


class KEventConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    tag = fields.SerializerMethodField()
    desc = serializers.CharField(source="comment")

    def get_tag(self, value):
        return "event"

    class Meta:
        model = KEvent
        fields = "id", "desc", "occurance_condition", "tag"


class KIntervalConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    tag = fields.SerializerMethodField()
    desc = serializers.CharField(source="comment")

    def get_tag(self, value):
        return "interval"

    class Meta:
        model = KInterval
        fields = "id", "desc", "open", "close", "tag"


class KRuleConvertSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="kb_id")
    desc = serializers.CharField(source="comment")
    instructions = AttrAsIsRelatedField(many=True, source="kr_instructions", attr="data", read_only=True)
    else_instructions = AttrAsIsRelatedField(many=True, source="kr_else_instructions", attr="data", read_only=True)
    tag = fields.SerializerMethodField()

    def get_tag(self, value):
        return "rule"

    class Meta:
        model = KRule
        fields = "id", "desc", "condition", "instructions", "else_instructions", "tag"
