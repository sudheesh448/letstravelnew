# Generated by Django 4.2.2 on 2023-07-21 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0030_alter_productvariantcolor_offer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='total_amount_cliamed',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='total_cliamed',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=5, null=True),
        ),
    ]
