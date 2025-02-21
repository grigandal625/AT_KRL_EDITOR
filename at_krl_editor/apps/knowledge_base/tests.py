from at_krl.core.fuzzy.membership_function import MembershipFunction
from at_krl.core.fuzzy.membership_function import MFPoint
from at_krl.core.kb_instruction import AssignInstruction
from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_reference import KBReference
from at_krl.core.kb_value import KBValue
from at_krl.core.temporal.kb_allen_operation import KBAllenOperation
from at_krl.core.temporal.utils import SimpleOperation
from at_krl.core.temporal.utils import SimpleReference
from at_krl.core.temporal.utils import SimpleValue
from django.test import TestCase
from knowledge_base.models import KEvent
from knowledge_base.models import KInterval
from knowledge_base.models import KnowledgeBase
from knowledge_base.models import KObject
from knowledge_base.models import KObjectAttribute
from knowledge_base.models import KRule
from knowledge_base.models import KRuleInstruction
from knowledge_base.models import KType
from knowledge_base.models import KTypeValue
from knowledge_base.service import KBService

# Create your tests here.


class TestKB(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_kb_serializing(self):
        k = KnowledgeBase.objects.create(name="test")
        t = KType.objects.create(kb_id="test_num", knowledge_base=k, meta=KType.MetaTypeChoices.NUMBER)
        KTypeValue.objects.create(type=t, data=5.0)
        KTypeValue.objects.create(type=t, data=10.0)
        nt = KBService.convert(t)
        print(nt.krl)

        t = KType.objects.create(kb_id="test_sym", knowledge_base=k, meta=KType.MetaTypeChoices.STRING)
        KTypeValue.objects.create(type=t, data="hello")
        KTypeValue.objects.create(type=t, data="goodbye")
        nt = KBService.convert(t)
        print(nt.krl)

        p1, p2, p3 = MFPoint(0, 1), MFPoint(2, 0.5), MFPoint(3, 0)
        p4, p5, p6 = MFPoint(0, 0), MFPoint(2, 0.5), MFPoint(3, 1)
        f1 = MembershipFunction("test_mf1", 0, 3, [p1, p2, p3])
        f2 = MembershipFunction("test_mf2", 0, 3, [p4, p5, p6])
        t = KType.objects.create(kb_id="test_fuzz", knowledge_base=k, meta=KType.MetaTypeChoices.FUZZY)
        KTypeValue.objects.create(type=t, data=f1.__dict__())
        KTypeValue.objects.create(type=t, data=f2.__dict__())
        nt = KBService.convert(t)
        print(nt.krl)

        o = KObject.objects.create(kb_id="test_obj", knowledge_base=k)
        KObjectAttribute.objects.create(kb_id="test_attr1", object=o, type=KType.objects.all()[0])
        KObjectAttribute.objects.create(kb_id="test_attr2", object=o, type=KType.objects.all()[1])
        KObjectAttribute.objects.create(kb_id="test_attr3", object=o, type=KType.objects.all()[2])
        no = KBService.convert(o)
        print(no.krl)

        occ_cnd = SimpleOperation.operation_class_by_sign("=")(
            "=", SimpleReference.parse("test_obj.test_attr1"), SimpleValue(7)
        )
        e = KEvent.objects.create(kb_id="test_event", knowledge_base=k, occurance_condition=occ_cnd.__dict__())
        ne = KBService.convert(e)
        print(ne.krl)

        open = SimpleOperation.operation_class_by_sign("=")(
            "=", SimpleReference.parse("test_obj.test_attr2"), SimpleValue("hello")
        )
        close = SimpleOperation.operation_class_by_sign("=")(
            "=", SimpleReference.parse("test_obj.test_attr3"), SimpleValue("test_mf1")
        )
        i = KInterval.objects.create(
            kb_id="test_interval", knowledge_base=k, open=open.__dict__(), close=close.__dict__()
        )
        ni = KBService.convert(i)
        print(ni.krl)

        first_op = KBOperation("=", KBReference.parse("test_obj.test_attr1"), KBValue(6))
        sec_op = KBAllenOperation("d", ne.id, ni.id)
        final_op = KBOperation("&", first_op, sec_op)
        instr = AssignInstruction(KBReference.parse("test_obj.test_attr3"), KBValue("test_mf3"))
        r = KRule.objects.create(kb_id="test_rule", knowledge_base=k, condition=final_op.__dict__())
        KRuleInstruction.objects.create(rule=r, data=instr.__dict__())
        nr = KBService.convert(r)
        print(nr.krl)
