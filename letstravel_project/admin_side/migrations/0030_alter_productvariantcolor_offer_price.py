# Generated by Django 4.2.2 on 2023-07-20 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0029_alter_productvariantcolor_offer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariantcolor',
            name='offer_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]