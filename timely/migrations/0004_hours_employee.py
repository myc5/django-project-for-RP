# Generated by Django 4.2.9 on 2024-02-02 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0003_remove_hours_employee_alter_hours_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='hours',
            name='employee',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]