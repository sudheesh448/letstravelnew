# Generated by Django 4.2.2 on 2023-07-01 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0004_alter_product_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='variants',
            field=models.ManyToManyField(through='admin_side.ProductVariant', to='admin_side.variant'),
        ),
    ]
