# Generated by Django 3.0.7 on 2021-03-23 11:04

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20210323_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='мобильный номер'),
        ),
    ]