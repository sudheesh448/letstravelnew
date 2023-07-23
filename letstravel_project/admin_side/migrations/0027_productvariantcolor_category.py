# Generated by Django 4.2.2 on 2023-07-20 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0026_rename_on_active_productvariantcolor_on_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariantcolor',
            name='category',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, to='admin_side.category'),
            preserve_default=False,
        ),
    ]