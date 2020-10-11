# Generated by Django 3.0.7 on 2020-10-11 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20201010_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1', 'Необработанный'), ('2', 'Выполняется'), ('3', 'В пути'), ('4', 'Доставлен'), ('5', 'Отменен')], default='1', max_length=2),
        ),
    ]