# Generated by Django 5.1.4 on 2024-12-16 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0027_newgamegenre_game_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='steam_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='Steam App ID'),
        ),
    ]
