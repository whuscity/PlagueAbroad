# Generated by Django 2.0.5 on 2020-04-30 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_auto_20200430_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articledata',
            name='is_public',
            field=models.IntegerField(blank=True, choices=[(0, '否'), (1, '是')], null=True, verbose_name='是否对外发布'),
        ),
        migrations.AlterField(
            model_name='articledata',
            name='is_put_top',
            field=models.IntegerField(blank=True, choices=[(0, '否'), (1, '是')], null=True, verbose_name='是否置顶'),
        ),
    ]
