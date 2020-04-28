# Generated by Django 2.0.5 on 2020-04-27 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OEC', '0005_auto_20200424_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='oecinfo',
            name='address',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='地址'),
        ),
        migrations.AddField(
            model_name='oecinfo',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='邮箱'),
        ),
        migrations.AddField(
            model_name='oecinfo',
            name='phone',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='电话'),
        ),
        migrations.AddField(
            model_name='oecinfo',
            name='url',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='网址'),
        ),
    ]
