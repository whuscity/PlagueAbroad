from django.db import models
from DjangoUeditor.models import UEditorField
from datetime import datetime

# Create your models here.
class ArticleSource(models.Model):
    name = models.CharField(max_length=50, verbose_name="数据源名称")
    link = models.CharField(max_length=100, verbose_name="数据源链接", null=True, blank=True)
    description = models.CharField(max_length=255, verbose_name="数据源描述", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "文章来源"
        verbose_name_plural = verbose_name

class ArticleData(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题', null=True, blank=True)
    is_public = models.IntegerField(verbose_name="是否对外发布", choices=((0, '否'), (1, '是'),(2, '待审核')), null=True, blank=True)
    is_put_top = models.IntegerField(verbose_name="是否置顶", choices=((0, '否'), (1, '是')), null=True, blank=True)
    direct_source = models.ForeignKey(ArticleSource, related_name="direct_source", verbose_name='直接来源', on_delete=models.CASCADE, null=True, blank=True)
    original_source = models.ForeignKey(ArticleSource, related_name="original_source", verbose_name='原始来源', on_delete=models.CASCADE, null=True, blank=True)
    original_source_name = models.CharField(max_length=200, verbose_name='原始机构', null=True, blank=True)
    nick_name = models.CharField(max_length=100, verbose_name='微博昵称', null=True, blank=True)
    url = models.CharField(max_length=500, verbose_name='原始链接', null=True, blank=True)
    abstract = models.TextField(max_length=300, verbose_name='摘要', null=True, blank=True)
    text = UEditorField(verbose_name='内容', width=600, height=700, toolbars="full", imagePath="ueditor/", filePath="ueditor/", blank=True, null=True)
    publish_time = models.DateTimeField(verbose_name='发布时间', null=True, blank=True, default=datetime.now())
    access_time = models.DateTimeField(max_length=150, verbose_name='获取时间', null=True, blank=True)
    location = models.CharField(max_length=50, verbose_name='国家地区', null=True, blank=True)
    type = models.CharField(choices=(('O', '官方要闻'), ('S', '海外信息'), ('R', '态势报告'), ('D', '抗疫日记')), max_length=10,
                              verbose_name="类型", null=True, blank=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
