# Generated by Django 2.0.5 on 2020-06-24 11:31

import DjangoUeditor.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0011_auto_20200624_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='content',
            field=DjangoUeditor.models.UEditorField(verbose_name='内容'),
        ),
        migrations.AlterField(
            model_name='content',
            name='publish_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 24, 11, 31, 39, 216298), verbose_name='发布时间'),
        ),
    ]