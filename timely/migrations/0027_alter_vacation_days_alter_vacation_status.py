# Generated by Django 4.2.9 on 2024-02-09 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timely', '0026_remove_vacation_approved_vacation_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacation',
            name='days',
            field=models.IntegerField(blank=True, verbose_name='Days (gets autocalculated)'),
        ),
        migrations.AlterField(
            model_name='vacation',
            name='status',
            field=models.CharField(choices=[('APPROVED', 'Approved'), ('PENDING', 'Pending'), ('DENIED', 'Denied')], default='PENDING', max_length=10),
        ),
    ]
