# Generated by Django 4.2.9 on 2024-02-02 13:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0006_delete_employees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hours',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 2)),
        ),
    ]
