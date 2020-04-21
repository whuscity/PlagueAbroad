# Generated by Django 2.0.5 on 2020-04-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direct_source', models.CharField(blank=True, max_length=200, null=True, verbose_name='直接来源')),
                ('origin_source', models.CharField(blank=True, max_length=200, null=True, verbose_name='原始来源')),
                ('origin_source_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='原始机构')),
                ('nick_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='微博昵称')),
                ('url', models.CharField(blank=True, max_length=500, null=True, verbose_name='原始链接')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('abstract', models.CharField(blank=True, max_length=300, null=True, verbose_name='摘要')),
                ('text', models.TextField(verbose_name='内容')),
                ('publish_time', models.CharField(max_length=150, verbose_name='发布时间')),
                ('access_time', models.CharField(max_length=150, verbose_name='获取时间')),
                ('location', models.CharField(blank=True, max_length=50, null=True, verbose_name='国家地区')),
                ('type', models.CharField(choices=[('O', '官方通告'), ('D', '抗议指南'), ('A', '风险预警')], max_length=10, verbose_name='类型')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
            },
        ),
    ]
