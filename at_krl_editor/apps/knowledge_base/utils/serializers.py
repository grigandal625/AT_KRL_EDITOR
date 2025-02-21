from rest_framework import serializers


class FMModelSerializer(serializers.ModelSerializer):
    field_name_map = {}

    def to_representation(self, instance):
        res = super().to_representation(instance)
        nres = res.__class__()
        for k, v in res.items():
            nres[self.field_name_map.get(k, k)] = v
        return nres


class AttrStringRelatedField(serializers.StringRelatedField):
    _attr = None

    def __init__(self, *, attr, **kwargs):
        self._attr = attr
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(getattr(value, self._attr))


class AttrAsIsRelatedField(serializers.RelatedField):
    _attr = None

    def __init__(self, *, attr, **kwargs):
        self._attr = attr
        super().__init__(**kwargs)

    def to_representation(self, value):
        return getattr(value, self._attr)
