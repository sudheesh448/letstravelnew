# Generated by Django 4.2.2 on 2023-07-01 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0006_remove_productvariantcolor_color_variant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariantcolor',
            name='color_variant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='admin_side.colorvariant'),
            preserve_default=False,
        ),
    ]
