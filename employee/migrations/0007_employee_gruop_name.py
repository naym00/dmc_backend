# Generated by Django 4.2.7 on 2024-01-04 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_employeegroupdevice_job_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='gruop_name',
            field=models.CharField(default='-', max_length=100, null=True),
        ),
    ]
