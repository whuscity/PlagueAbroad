from django.db import models
from DjangoUeditor.models import UEditorField

# Create your models here.

class Content(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = UEditorField(width=600, height=700, toolbars="full", imagePath="report/", filePath="report/", blank=True, null=True)
    publish_time = models.DateTimeField(verbose_name='发布时间')
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    is_put_top = models.IntegerField(verbose_name="是否置顶", choices=((0, '否'), (1, '是')), null=True, blank=True)

    def __str__(self):
        return  self.title

