# Generated by Django 5.0.2 on 2024-03-07 03:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('game', '0013_delete_featuredgame'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50)),
                ('tag_color_code', models.CharField(max_length=7)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.game')),
            ],
        ),
    ]
