# Generated by Django 4.2.2 on 2023-07-20 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0015_categoryoffer_usercategoryoffer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryoffer',
            old_name='expiry',
            new_name='expiry_date',
        ),
    ]
