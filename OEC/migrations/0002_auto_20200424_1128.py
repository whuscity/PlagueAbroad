# Generated by Django 2.0.5 on 2020-04-24 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OEC', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oecinfo',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='使馆名称'),
        ),
    ]
