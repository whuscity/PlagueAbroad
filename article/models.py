from django.db import models

# Create your models here.
class ArticleModel(models.Model):
    direct_source = models.CharField(max_length=200, verbose_name='直接来源', null=True, blank=True)
    origin_source = models.CharField(max_length=200, verbose_name='原始来源', null=True, blank=True)
    origin_source_name = models.CharField(max_length=200, verbose_name='原始机构', null=True, blank=True)
    nick_name = models.CharField(max_length=100, verbose_name='微博昵称', null=True, blank=True)
    url = models.CharField(max_length=500, verbose_name='原始链接', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name='标题')
    abstract = models.CharField(max_length=300, verbose_name='摘要', null=True, blank=True)
    text = models.TextField(verbose_name='内容')
    publish_time = models.CharField(max_length=150, verbose_name='发布时间')
    access_time = models.CharField(max_length=150, verbose_name='获取时间')
    location = models.CharField(max_length=50, verbose_name='国家地区', null=True, blank=True)
    type = models.CharField(choices=(('O', '官方通告'), ('D', '抗议指南'), ('A', '风险预警')), max_length=10,
                              verbose_name="类型")

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
