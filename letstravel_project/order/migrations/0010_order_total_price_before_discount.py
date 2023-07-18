# Generated by Django 4.2.2 on 2023-07-18 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_order_razorpay_payment_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price_before_discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
