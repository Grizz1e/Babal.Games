# Generated by Django 5.0.2 on 2024-03-04 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_alter_gameorder_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameorder',
            name='pidx',
            field=models.CharField(default='', max_length=100),
        ),
    ]