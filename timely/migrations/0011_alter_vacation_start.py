# Generated by Django 4.2.9 on 2024-02-06 12:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0010_alter_hours_time_vacation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='start',
            field=models.DateField(default=datetime.datetime(2024, 2, 6, 12, 20, 53, 414761, tzinfo=datetime.timezone.utc)),
        ),
    ]