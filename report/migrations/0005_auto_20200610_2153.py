# Generated by Django 2.0.5 on 2020-06-10 21:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0004_auto_20200610_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='publish_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 10, 21, 53, 21, 824542), verbose_name='发布时间'),
        ),
    ]
