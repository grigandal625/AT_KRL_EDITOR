from django.urls import include
from django.urls import path
from rest_framework_nested import routers

from at_krl_editor.apps.knowledge_base import views

router = routers.SimpleRouter()
router.register(r"knowledge_bases", views.KnowledgeBaseViewSet)

kb_router = routers.NestedSimpleRouter(router, "knowledge_bases", lookup="knowledge_base")
kb_router.register(r"k_types", views.KTypeViewSet)

kt_router = routers.NestedSimpleRouter(kb_router, "k_types", lookup="k_type")
kt_router.register(r"kt_values", views.KTypeValueViewSet)

kb_router.register(r"k_objects", views.KObjectViewSet)
kb_router.register(r"k_intervals", views.KIntervalViewSet)
kb_router.register(r"k_events", views.KEventViewSet)

ko_router = routers.NestedSimpleRouter(kb_router, "k_objects", lookup="k_object")
ko_router.register(r"ko_attributes", views.KObjectAttributeViewSet)


kb_router.register(r"k_rules", views.KRuleViewSet)

kr_router = routers.NestedSimpleRouter(kb_router, "k_rules", lookup="k_rule")
kr_router.register(r"kr_instructions", views.KRuleInstructionViewSet)
kr_router.register(r"kr_else_instructions", views.KRuleElseInstructionViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(kb_router.urls)),
    path(r"", include(kt_router.urls)),
    path(r"", include(ko_router.urls)),
    path(r"", include(kr_router.urls)),
]
