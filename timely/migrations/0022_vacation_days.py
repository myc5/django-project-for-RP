# Generated by Django 4.2.9 on 2024-02-08 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0021_vacation_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='days',
            field=models.IntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
