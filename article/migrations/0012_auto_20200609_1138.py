# Generated by Django 2.0.5 on 2020-06-09 11:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0011_auto_20200609_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articledata',
            name='publish_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 6, 9, 11, 38, 41, 204843), null=True, verbose_name='发布时间'),
        ),
        migrations.AlterField(
            model_name='articledata',
            name='type',
            field=models.CharField(blank=True, choices=[('O', '官方要闻'), ('S', '海外信息'), ('R', '态势报告'), ('D', '抗疫日记')], max_length=10, null=True, verbose_name='类型'),
        ),
    ]
