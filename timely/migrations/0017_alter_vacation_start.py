# Generated by Django 4.2.9 on 2024-02-07 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0016_alter_vacation_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='start',
            field=models.DateField(),
        ),
    ]
