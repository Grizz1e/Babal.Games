# Generated by Django 5.0.2 on 2024-03-07 03:18

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_remove_basket_total_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='games',
        ),
        migrations.CreateModel(
            name='GameVoucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_code', models.CharField(max_length=20, unique=True)),
                ('voucher_type', models.CharField(choices=[('percentage', 'Percentage'), ('amount', 'Amount')], default='percentage', max_length=10)),
                ('max_discount_amount', models.FloatField()),
                ('percentage_discount', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('used_by', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Basket',
        ),
        migrations.DeleteModel(
            name='Wishlist',
        ),
    ]
