# Generated by Django 4.2.7 on 2024-01-24 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_alter_devices_device_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='devices',
            name='password',
            field=models.CharField(blank=True, default='admin', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='devices',
            name='username',
            field=models.CharField(blank=True, default='admin', max_length=100, null=True),
        ),
    ]
