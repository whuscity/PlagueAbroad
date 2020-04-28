from django.db import models

# Create your models here.

class OECInfo(models.Model):
    region = models.CharField(max_length=50, verbose_name="区域", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="使馆名称", null=True, blank=True)
    related_info = models.TextField(max_length=1000, verbose_name="相关信息", null=True, blank=True)
    address = models.CharField(max_length=200, verbose_name="地址", null=True, blank=True)
    phone = models.CharField(max_length=100, verbose_name="电话", null=True, blank=True)
    url = models.CharField(max_length=50, verbose_name="网址", null=True, blank=True)
    email = models.CharField(max_length=50, verbose_name="邮箱", null=True, blank=True)
    type = models.IntegerField(choices=((0, '驻外使馆'), (1, '驻外总领馆'), (2, '驻外团、处')),
                              verbose_name="使馆类型", null=True, blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "使馆信息"
        verbose_name_plural = verbose_name
