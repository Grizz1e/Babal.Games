# Generated by Django 5.0.2 on 2024-03-04 11:31

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_alter_gameorder_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameorder',
            name='order_id',
            field=models.UUIDField(auto_created=True, default=uuid.UUID('f2349bac-e7b3-48ec-95ef-7b433ea8d756'), editable=False, unique=True),
        ),
    ]
