# Generated by Django 3.1.2 on 2021-03-01 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_auto_20210215_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='ninja',
            name='ninja_bank',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='ninja',
            name='ninja_age',
            field=models.IntegerField(default=0),
        ),
    ]