import sqlalchemy
import pymysql
import xadmin
from .models import ArticleSource, ArticleData
from  xadmin import  views
from  datetime import  datetime
import  numpy as np

from PlagueAbroad.settings import DATABASES
from xadmin.views.edit import UpdateAdminView


import  pandas as pd

class BaseXadminSettings(object):
    # 添加主题选择功能
    enable_themes = True
    # 添加多个选项到主题选择中
    use_bootswatch = True

class CommonXadminSettings(object):
    site_title = '海外疫情信息集成平台后台管理'
    site_footer = '鄂ICP备15018236号-5'
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
                if str(item.get('description')) == 'nan':
                    case.description = None
                if case.id not in idxs_d:
                    sources.append(case)
            if sources:
                ArticleSource.objects.bulk_create(sources)



        return super(ArticleSourceAdmin, self).post(request, args, kwargs)



class ArticleDataAdmin(object):
    list_display = ['title', 'original_source_name',  'type', 'is_public', 'is_put_top', 'publish_time']
    list_filter = ['original_source_name', 'title', 'location', 'access_time' ,'is_public', 'is_put_top', 'type']
    style_fields = {"text": "ueditor"}
    list_editable = ['is_public', 'is_put_top', 'type']
    import_csv = True

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            file = request.FILES.get('excel')
            data_df = pd.read_csv(file, encoding='utf-8')
            sources = []
            idxs = ArticleData.objects.all().values('id')
            urls = ArticleData.objects.all().values('url')
            print(idxs)
            print(urls)
            idxs_d = dict([(d['id'], True) for d in idxs])
            urls_list = dict([(d['url'], True) for d in urls])
            for index, item in data_df.iterrows():
                case = ArticleData()
                case.id = item.get('id')
                case.direct_source_id = item.get('direct_source_id')
                # case.original_source_id = item.get('original_source_id')
                if str(item.get('original_source_id')) == 'nan':
                    case.original_source_id = None
                else:
                    case.original_source_id = int(item.get('original_source_id'))
                case.original_source_name = item.get('original_source_name')
                case.nick_name = item.get('nick_name')
                if str(item.get('nick_name')) == 'nan':
                    case.nick_name = None
                case.url = item.get('url')
                case.title = item.get('title')
                case.abstract = item.get('abstract')
                case.text = item.get('text')
                publish_time = datetime.strptime(item.get('publish_time'), "%d/%m/%Y %H:%M:%S")
                print(publish_time)
                case.publish_time = datetime.strftime(publish_time, "%Y-%m-%d %H:%M:%S")
                # print(case.publish_time)
                access_time = datetime.strptime(item.get('access_time'), "%d/%m/%Y %H:%M:%S")
                print(access_time)
                case.access_time = datetime.strftime(access_time, "%Y-%m-%d %H:%M:%S")
                # case.access_time = item.get('access_time')
                case.location = item.get('location')
                type2char = {'官方通告': 'O', '抗疫指南':'D', '风险预警':'A'}
                case.type = type2char.get(item.get('type'))

                # public_dict = {'否': 0, '是': 1, '待审核': 2}
                # case.is_public = public_dict.get(item.get('is_public'))
                case.is_public = 2
                # top_dict = {'否': 0, '是': 1}
                # case.is_put_top = top_dict.get(item.get('is_put_top'))
                case.is_put_top = 0

                if case.id not in idxs_d and case.url not in urls_list:
                    sources.append(case)
            if sources:
                ArticleData.objects.bulk_create(sources)
        return super(ArticleDataAdmin, self).post(request, *args, **kwargs)
        # return super(UpdateAdminView, self).post(request, *args, **kwargs)

xadmin.site.register(ArticleSource, ArticleSourceAdmin)
xadmin.site.register(ArticleData, ArticleDataAdmin)
xadmin.site.register(views.CommAdminView, CommonXadminSettings)
xadmin.site.register(views.BaseAdminView, BaseXadminSettings)