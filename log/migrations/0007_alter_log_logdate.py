# Generated by Django 4.2.7 on 2024-01-03 11:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0006_alter_log_logdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='logdate',
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]