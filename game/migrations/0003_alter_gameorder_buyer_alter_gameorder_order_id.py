# Generated by Django 5.0.2 on 2024-03-04 11:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_gameorder_order_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameorder',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='gameorder',
            name='order_id',
            field=models.UUIDField(blank=True, default='7948b5442f8e4352b978028a5a48ffbb', editable=False, null=True),
        ),
    ]