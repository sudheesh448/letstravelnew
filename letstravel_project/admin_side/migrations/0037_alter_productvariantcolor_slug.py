# Generated by Django 4.2.2 on 2023-08-01 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0036_alter_productvariantcolor_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariantcolor',
            name='slug',
            field=models.SlugField(max_length=300, unique=True),
        ),
    ]
