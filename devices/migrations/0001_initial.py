# Generated by Django 4.2.7 on 2023-12-20 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('device_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('device_name', models.CharField(default='-', max_length=100)),
                ('location', models.CharField(default='-', max_length=100, null=True)),
                ('device_ip', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('active_status', models.CharField(default='inactive', max_length=100)),
            ],
        ),
    ]
