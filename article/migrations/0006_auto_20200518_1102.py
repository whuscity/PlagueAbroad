# Generated by Django 2.0.5 on 2020-05-18 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0005_auto_20200518_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articledata',
            name='is_public',
            field=models.IntegerField(blank=True, choices=[(0, '否'), (1, '是')], null=True, verbose_name='是否对外发布'),
        ),
    ]
