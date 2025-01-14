# Generated by Django 5.1.4 on 2025-01-10 06:51

import django.utils.timezone
import game.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0039_gamebuild'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamebuild',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='gamebuild',
            name='zip_file',
            field=models.FileField(storage=game.models.OutsideMediaStorage, upload_to=game.models.game_build_upload),
        ),
    ]
