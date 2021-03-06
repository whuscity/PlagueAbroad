# Generated by Django 2.0.5 on 2020-04-24 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OECInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, max_length=50, null=True, verbose_name='驻外使馆')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='使馆名称')),
                ('related_info', models.TextField(blank=True, max_length=1000, null=True, verbose_name='相关信息')),
            ],
            options={
                'verbose_name': '使馆信息',
                'verbose_name_plural': '使馆信息',
            },
        ),
    ]
