# Generated by Django 4.2.9 on 2024-02-08 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0024_rename_approval_status_vacation_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='days',
            field=models.IntegerField(blank=True, default=0, verbose_name='Gets autocalculated, do not touch'),
            preserve_default=False,
        ),
    ]
