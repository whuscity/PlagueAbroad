# Generated by Django 2.0.5 on 2020-04-27 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OEC', '0006_auto_20200427_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oecinfo',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='地址'),
        ),
    ]
