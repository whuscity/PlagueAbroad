# Generated by Django 2.0.5 on 2020-04-24 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OEC', '0003_auto_20200424_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oecinfo',
            name='name',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='使馆名称'),
        ),
    ]
