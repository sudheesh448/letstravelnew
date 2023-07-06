# Generated by Django 4.2.2 on 2023-07-05 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0015_alter_productvariantcolor_slug'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='ProductVariantColor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='admin_side.productvariantcolor'),
            preserve_default=False,
        ),
    ]
