# Generated by Django 4.2.9 on 2024-06-30 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0014_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Создан'), (2, 'Обработан'), (3, 'Подтвержден'), (4, 'Отменен')], default=1, null=True, verbose_name='Статус'),
        ),
    ]
