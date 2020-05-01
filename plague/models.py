from django.db import models

# Create your models here.

class Global(models.Model):
    confirmed = models.BigIntegerField(verbose_name="确诊数")
    deaths = models.IntegerField(verbose_name="死亡数")
    recovered = models.BigIntegerField(verbose_name="治愈数")
    day_date = models.CharField(verbose_name="日期", max_length=50)
    update_time = models.CharField(verbose_name="更新时间", max_length=50)

    class Meta:
        db_table = "global"
        verbose_name = "全球疫情数据"
        verbose_name_plural = verbose_name

class RegionBasicInfo(models.Model):
    region = models.CharField(verbose_name="地区名称", max_length=100)
    region_chinese = models.CharField(verbose_name="地区中文名称", max_length=50, null=True, blank=True)
    region_code = models.CharField(verbose_name="地区代码", max_length=10, null=True, blank=True)
    region_parent_id = models.IntegerField(verbose_name="地区父ID", null=True, blank=True)
    region_level = models.IntegerField(verbose_name="地区级别", choices=((1, '国家'), (2, '省/州'), (3, '市')))

    class Meta:
        db_table = "region_basic_info"
        verbose_name = "地区基本信息"
        verbose_name_plural = verbose_name

class RegionData(models.Model):
    # region = models.ForeignKey(RegionBasicInfo, verbose_name="地区ID", on_delete=models.CASCADE)
    region_id = models.IntegerField(verbose_name="地区ID", null=True, blank=True)
    confirmed = models.BigIntegerField(verbose_name="确诊数")
    deaths = models.IntegerField(verbose_name="死亡数")
    recovered = models.BigIntegerField(verbose_name="治愈数")
    day_date = models.CharField(verbose_name="日期", max_length=50)
    last_updated = models.CharField(verbose_name="更新时间", max_length=50)

    class Meta:
        db_table = "region_data"
        verbose_name = "地区疫情数据"
        verbose_name_plural = verbose_name
