# Generated by Django 5.1.4 on 2024-12-18 05:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0035_gameorder_voucher_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamereview',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='game.game'),
        ),
    ]
