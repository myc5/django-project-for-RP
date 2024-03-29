# Generated by Django 4.2.9 on 2024-02-06 12:11

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timely', '0009_alter_hours_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hours',
            name='time',
            field=models.FloatField(choices=[(0.25, '15 mins'), (0.5, '30 mins'), (0.75, '45 mins'), (1.0, '1h'), (1.25, '1h 15 mins'), (1.5, '1h 30 mins'), (1.75, '1h 45 mins'), (2.0, '2h'), (2.25, '2h 15 mins'), (2.5, '2h 30 mins'), (2.75, '2h 45 mins'), (3.0, '3h'), (3.25, '3h 15 mins'), (3.5, '3h 30 mins'), (3.75, '3h 45 mins'), (4.0, '4h'), (4.25, '4h 15 mins'), (4.5, '4h 30 mins'), (4.75, '4h 45 mins'), (5.0, '5h'), (6.25, '6h 15 mins'), (6.5, '6h 30 mins'), (6.75, '6h 45 mins'), (7.0, '7h'), (7.25, '7h 15 mins'), (7.5, '7h 30 mins'), (7.75, '7h 45 mins'), (8.0, '8h'), (8.25, '8h 15 mins'), (8.5, '8h 30 mins'), (8.75, '8h 45 mins'), (9.0, '9h'), (9.25, '9h 15 mins'), (9.5, '9h 30 mins'), (9.75, '9h 45 mins'), (10.0, '10h'), (10.25, '10h 15 mins'), (10.5, '10h 30 mins'), (10.75, '10h 45 mins'), (11.0, '11h'), (11.25, '11h 15 mins'), (11.5, '11h 30 mins'), (11.75, '11h 45 mins'), (12.0, '12h')]),
        ),
        migrations.CreateModel(
            name='Vacation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(default=datetime.datetime(2024, 2, 6, 12, 11, 29, 867727, tzinfo=datetime.timezone.utc))),
                ('end', models.DateField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
