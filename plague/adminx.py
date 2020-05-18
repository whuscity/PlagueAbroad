import sqlalchemy
import pymysql
import xadmin
import pandas as pd

from .models import Global, RegionBasicInfo, RegionData

class GlobalAdmin(object):
    list_display = ['confirmed', 'deaths', 'recovered', 'day_date', 'update_time']
    list_filter = ['confirmed', 'deaths', 'recovered', 'day_date', 'update_time']

class RegionBasicInfoAdmin(object):
    list_display = ['id', 'region', 'region_chinese', 'region_parent_id', 'region_level']
    list_filter = ['region', 'region_chinese', 'region_parent_id', 'region_level']
    readonly_fields = ['id']

class RegionDataAdmin(object):
    list_display = ['region_id', 'confirmed', 'deaths', 'recovered', 'day_date', 'last_updated']
    list_filter = ['region_id', 'confirmed', 'deaths', 'recovered', 'day_date', 'last_updated']
    # readonly_fields = ['region_id']

xadmin.site.register(Global, GlobalAdmin)
xadmin.site.register(RegionBasicInfo, RegionBasicInfoAdmin)
xadmin.site.register(RegionData, RegionDataAdmin)