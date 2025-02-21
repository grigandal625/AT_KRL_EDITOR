# Generated by Django 5.1.6 on 2025-02-19 14:52
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="KnowledgeBase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("problem_area", models.TextField(blank=True, default=None, null=True)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("status", models.IntegerField(choices=[(1, "Загрузка"), (2, "Ок"), (3, "Ошибка")], default=2)),
                ("error", models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="KInterval",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("open", models.JSONField(blank=True, null=True)),
                ("close", models.JSONField(blank=True, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="k_intervals",
                        to="knowledge_base.knowledgebase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("occurance_condition", models.JSONField(blank=True, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="k_events",
                        to="knowledge_base.knowledgebase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KObject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("group", models.CharField(blank=True, default="ГРУППА1", max_length=255, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="k_objects",
                        to="knowledge_base.knowledgebase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("condition", models.JSONField(blank=True, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="k_rules",
                        to="knowledge_base.knowledgebase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KRuleElseInstruction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.JSONField()),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kr_else_instructions",
                        to="knowledge_base.krule",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KRuleInstruction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.JSONField()),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kr_instructions",
                        to="knowledge_base.krule",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("meta", models.IntegerField(choices=[(1, "String"), (2, "Number"), (3, "Fuzzy")])),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="k_types",
                        to="knowledge_base.knowledgebase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KObjectAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kb_id", models.CharField(max_length=255)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ko_attributes",
                        to="knowledge_base.kobject",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="ko_attributes",
                        to="knowledge_base.ktype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KTypeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.JSONField()),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="kt_values", to="knowledge_base.ktype"
                    ),
                ),
            ],
        ),
    ]
