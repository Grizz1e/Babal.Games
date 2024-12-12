# Generated by Django 5.0.2 on 2024-03-14 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0019_alter_gamecode_associated_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='video_id',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='game',
            name='youtube_trailer',
            field=models.URLField(blank=True),
        ),
    ]
