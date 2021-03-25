# Generated by Django 3.0.7 on 2021-03-25 04:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_auto_20210325_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дозвон'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='доставлен'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.IntegerField(choices=[(0, 'Наличными курьеру'), (1, 'Интернет-оплата'), (2, 'Картой курьеру')], db_index=True, default=0, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='поступил'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'Отменен'), (1, 'Необработанный'), (2, 'Выполняется'), (3, 'В пути'), (4, 'Доставлен')], db_index=True, default=1, verbose_name='статус'),
        ),
    ]