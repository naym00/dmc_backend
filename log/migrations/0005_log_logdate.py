# Generated by Django 4.2.7 on 2024-01-03 11:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0004_log_last_synced'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='logdate',
            field=models.DateField(default=datetime.datetime(2024, 1, 3, 17, 14, 27, 570307), null=True),
        ),
    ]
