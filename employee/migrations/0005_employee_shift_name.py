# Generated by Django 4.2.7 on 2023-12-28 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0004_employee_department_name_employee_designation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='shift_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]