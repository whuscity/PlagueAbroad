# Generated by Django 2.0.5 on 2020-06-10 21:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20200610_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='publish_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 10, 21, 50, 39, 742687), verbose_name='发布时间'),
        ),
    ]
