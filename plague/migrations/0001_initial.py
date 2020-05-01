# Generated by Django 2.0.5 on 2020-05-01 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Global',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BigIntegerField(verbose_name='确诊数')),
                ('deaths', models.IntegerField(verbose_name='死亡数')),
                ('recovered', models.BigIntegerField(verbose_name='治愈数')),
                ('day_date', models.DateField(verbose_name='日期')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '全球疫情数据',
                'verbose_name_plural': '全球疫情数据',
                'db_table': 'global',
            },
        ),
        migrations.CreateModel(
            name='RegionBasicInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=100, verbose_name='地区名称')),
                ('region_chinese', models.CharField(blank=True, max_length=50, null=True, verbose_name='地区中文名称')),
                ('region_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='地区代码')),
                ('region_parent_id', models.IntegerField(blank=True, null=True, verbose_name='地区父ID')),
                ('region_level', models.IntegerField(choices=[(1, '国家'), (2, '省/州'), (3, '市')], verbose_name='地区级别')),
            ],
            options={
                'verbose_name': '地区基本信息',
                'verbose_name_plural': '地区基本信息',
                'db_table': 'region_basic_info',
            },
        ),
        migrations.CreateModel(
            name='RegionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BigIntegerField(verbose_name='确诊数')),
                ('deaths', models.IntegerField(verbose_name='死亡数')),
                ('recovered', models.BigIntegerField(verbose_name='治愈数')),
                ('day_date', models.DateField(verbose_name='日期')),
                ('last_updated', models.DateTimeField(verbose_name='更新时间')),
                ('region_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plague.RegionBasicInfo', verbose_name='地区ID')),
            ],
            options={
                'verbose_name': '地区疫情数据',
                'verbose_name_plural': '地区疫情数据',
                'db_table': 'region_data',
            },
        ),
    ]