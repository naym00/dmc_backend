# Generated by Django 4.2.7 on 2024-01-03 11:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0005_log_logdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='logdate',
            field=models.DateField(default=datetime.date(2024, 1, 3), null=True),
        ),
    ]
