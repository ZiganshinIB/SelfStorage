# Generated by Django 5.0.6 on 2024-07-02 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0019_alter_rent_from_city_alter_rent_from_street_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='delivery',
            field=models.BooleanField(default=False, verbose_name='Доставка'),
        ),
    ]