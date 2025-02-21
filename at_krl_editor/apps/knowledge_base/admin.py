from django.contrib import admin

from at_krl_editor.apps.knowledge_base import models

# Register your models here.


@admin.register(models.KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = "id", "name", "status"
    search_fields = ("name",)
    list_filter = ("status",)


@admin.register(models.KType)
class KTypeAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "meta", "comment", "knowledge_base"
    search_fields = "kb_id", "comment"
    list_filter = ("meta",)


@admin.register(models.KTypeValue)
class KTypeValueAdmin(admin.ModelAdmin):
    list_display = "id", "data", "type"


@admin.register(models.KObject)
class KObjectAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "comment", "knowledge_base"
    search_fields = "kb_id", "comment"


@admin.register(models.KObjectAttribute)
class KObjectAttributeAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "type", "comment", "object"
    search_fields = "kb_id", "comment"


@admin.register(models.KInterval)
class KIntervalAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "comment", "knowledge_base"
    search_fields = "kb_id", "comment"


@admin.register(models.KEvent)
class KEventAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "comment", "knowledge_base"
    search_fields = "kb_id", "comment"


@admin.register(models.KRule)
class KRuleAdmin(admin.ModelAdmin):
    list_display = "id", "kb_id", "comment", "knowledge_base"
    search_fields = "kb_id", "comment"


@admin.register(models.KRuleInstruction)
class KRuleInstructionAdmin(admin.ModelAdmin):
    list_display = "id", "data", "rule"


@admin.register(models.KRuleElseInstruction)
class KRuleElseInstructionAdmin(admin.ModelAdmin):
    list_display = "id", "data", "rule"
