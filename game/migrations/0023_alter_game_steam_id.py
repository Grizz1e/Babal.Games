# Generated by Django 5.0.2 on 2024-03-29 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0022_game_steam_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='steam_id',
            field=models.CharField(max_length=10, verbose_name='Steam App ID'),
        ),
    ]
