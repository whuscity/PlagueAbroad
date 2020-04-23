import sqlalchemy
import pymysql
import xadmin
from .models import ArticleSource, ArticleData
from  xadmin import  views

from PlagueAbroad.settings import DATABASES


import  pandas as pd

class BaseXadminSettings(object):
    # 添加主题选择功能
    enable_themes = True
    # 添加多个选项到主题选择中
    use_bootswatch = True

class CommonXadminSettings(object):
    site_title = '海外疫情信息集成平台后台管理'
    site_footer = 'whuscity'
    menu_style = 'accordion'

class ArticleSourceAdmin(object):
    list_display = ['name', 'link', 'description']
    list_filter = ['name']
    import_csv = True

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            file = request.FILES.get('excel')
            data_df = pd.read_csv(file, encoding='utf-8')
            sources = []
            idxs = ArticleSource.objects.all().values('id')
            idxs_d = dict([(d['id'], True) for d in idxs])
            for index, item in data_df.iterrows():
                case = ArticleSource()
                case.id = item.get('id')
                case.name = item.get('name')
                case.link = item.get('link')
                case.description = item.get('description')
                if case.id not in idxs_d:
                    sources.append(case)
            if sources:
                ArticleSource.objects.bulk_create(sources)



        return super(ArticleSourceAdmin, self).post(request, args, kwargs)



class ArticleDataAdmin(object):
    list_display = ['title', 'original_source_name', 'publish_time']
    list_filter = ['original_source_name', 'title', 'location', 'type']
    style_fields = {"text": "ueditor"}
    import_csv = True

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            file = request.FILES.get('excel')
            data_df = pd.read_csv(file, encoding='utf-8')
            sources = []
            idxs = ArticleData.objects.all().values('id')
            idxs_d = dict([(d['id'], True) for d in idxs])
            for index, item in data_df.iterrows():
                case = ArticleData()
                case.id = item.get('id')
                case.direct_source = item.get('direct_source')
                case.original_source = item.get('original_source')
                case.nick_name = item.get('nick_name')
                case.url = item.get('url')
                case.title = item.get('title')
                case.abstract = item.get('abstract')
                case.text = item.get('text')
                case.publish_time = item.get('publish_time')
                case.access_time = item.get('access_time')
                case.location = item.get('location')
                type2char = {'官方通告': 'O', '抗疫指南':'D', '风险预警':'A'}
                case.type = type2char.get(item.get('type'))
                if case.id not in idxs_d:
                    sources.append(case)
            if sources:
                ArticleData.objects.bulk_create(sources)
        return super(ArticleDataAdmin, self).post(request, args, kwargs)

xadmin.site.register(ArticleSource, ArticleSourceAdmin)
xadmin.site.register(ArticleData, ArticleDataAdmin)
xadmin.site.register(views.CommAdminView, CommonXadminSettings)
xadmin.site.register(views.BaseAdminView, BaseXadminSettings)