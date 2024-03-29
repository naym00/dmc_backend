# Generated by Django 4.2.7 on 2023-12-20 05:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ForgetPassword',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(default='example@gmail.com', max_length=254)),
                ('token', models.TextField()),
                ('creation_date', models.DateTimeField()),
                ('expiration_date', models.DateTimeField()),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
