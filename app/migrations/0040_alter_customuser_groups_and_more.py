# Generated by Django 5.2 on 2025-05-04 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0039_alter_customuser_profile_pic"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to.",
                related_name="custom_user_set",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="custom_user_set",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="app.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="parent",
            name="admin",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="app.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="staff",
            name="admin",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="app.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="admin",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="app.customuser"
            ),
        ),
    ]
