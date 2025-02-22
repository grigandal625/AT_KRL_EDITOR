from adrf import serializers
from adrf.fields import aget_attribute
from adrf.relations import StringRelatedField, RelatedField


class FMModelSerializer(serializers.ModelSerializer):
    field_name_map = {}

    def to_representation(self, instance):
        res = super().to_representation(instance)
        nres = res.__class__()
        for k, v in res.items():
            nres[self.field_name_map.get(k, k)] = v
        return nres

    async def ato_representation(self, instance):
        res = await super().ato_representation(instance)
        nres = res.__class__()
        for k, v in res.items():
            nres[self.field_name_map.get(k, k)] = v
        return nres


class AttrStringRelatedField(StringRelatedField):
    _attr = None

    def __init__(self, *, attr, **kwargs):
        self._attr = attr
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(getattr(value, self._attr))

    async def ato_representation(self, value):
        return str(await aget_attribute(value, [self._attr]))


class AttrAsIsRelatedField(RelatedField):
    _attr = None

    def __init__(self, *, attr, **kwargs):
        self._attr = attr
        super().__init__(**kwargs)

    def to_representation(self, value):
        return getattr(value, self._attr)

    async def ato_representation(self, value):
        return await aget_attribute(value, [self._attr])
