# Generated by Django 3.0.7 on 2021-03-25 03:43

from django.db import migrations
from phonenumber_field.modelfields import PhoneNumberField


def fill_new_phonenumber_field(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    orders = []
    for order in Order.objects.all():
        order.new_phonenumber = PhoneNumberField().get_prep_value(
            order.phonenumber,
        )
        orders.append(order)
    Order.objects.bulk_update(orders, ['new_phonenumber'])


def move_backward(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    orders = []
    for order in Order.objects.all():
        order.phonenumber = order.new_phonenumber
        orders.append(order)
    Order.objects.bulk_update(orders, ['phonenumber'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_new_phonenumber'),
    ]

    operations = [
        migrations.RunPython(fill_new_phonenumber_field, move_backward),
    ]
