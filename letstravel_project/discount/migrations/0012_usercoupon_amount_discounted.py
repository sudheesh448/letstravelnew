# Generated by Django 4.2.2 on 2023-07-17 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0011_alter_coupon_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoupon',
            name='amount_discounted',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]