# Generated by Django 4.2.2 on 2023-07-06 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cart_id',
            field=models.FloatField(unique=True),
        ),
    ]
