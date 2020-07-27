from django.db import models
from DjangoUeditor.models import UEditorField
from datetime import datetime

# Create your models here.

class Content(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = UEditorField(width=600, height=800, toolbars="full", imagePath="report/", filePath="report/", verbose_name='内容')
    publish_time = models.DateTimeField(verbose_name='发布时间', default=datetime.now())
    wechat_url = models.CharField(max_length=255, verbose_name='微信链接', null=True, blank=True)
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    type = models.CharField(choices=(('R', '态势分析'), ('D', '专题报告')), max_length=10,
                              verbose_name="类型")
    is_put_top = models.IntegerField(verbose_name="是否置顶", choices=((0, '否'), (1, '是')))

    def __str__(self):
        return  self.title

    class Meta:
        verbose_name = '内容管理'
        verbose_name_plural = verbose_name