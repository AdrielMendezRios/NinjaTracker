# Generated by Django 3.1.2 on 2020-11-06 17:36

from django.db import migrations
import tracker.models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='employee',
            managers=[
                ('objects', tracker.models.EmployeeManager()),
            ],
        ),
    ]
