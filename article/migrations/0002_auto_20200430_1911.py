# Generated by Django 2.0.5 on 2020-04-30 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='articledata',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='是否对外发布'),
        ),
        migrations.AddField(
            model_name='articledata',
            name='is_put_top',
            field=models.BooleanField(default=False, verbose_name='是否置顶'),
        ),
        migrations.AlterField(
            model_name='articledata',
            name='abstract',
            field=models.TextField(blank=True, max_length=300, null=True, verbose_name='摘要'),
        ),
    ]
