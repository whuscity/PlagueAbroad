# Generated by Django 2.0.5 on 2020-06-24 11:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_auto_20200624_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='publish_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 24, 11, 29, 38, 719927), verbose_name='发布时间'),
        ),
    ]