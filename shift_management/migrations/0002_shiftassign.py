# Generated by Django 4.2.7 on 2023-12-26 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shift_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftAssign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('shift_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_management.shiftmanagement')),
            ],
        ),
    ]
