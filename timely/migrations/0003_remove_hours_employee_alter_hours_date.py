# Generated by Django 4.2.9 on 2024-02-02 07:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0002_alter_clients_options_alter_employees_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hours',
            name='employee',
        ),
        migrations.AlterField(
            model_name='hours',
            name='date',
            field=models.CharField(default=datetime.date(2024, 2, 2), max_length=200),
        ),
    ]
