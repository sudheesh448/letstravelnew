# Generated by Django 4.2.2 on 2023-07-25 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0033_phonenumber_referred_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariantcolor',
            name='product',
            field=models.ForeignKey( on_delete=django.db.models.deletion.CASCADE, to='admin_side.product'),
            preserve_default=False,
        ),
    ]
