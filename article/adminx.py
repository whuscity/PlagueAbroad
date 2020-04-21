import xadmin
from .models import ArticleSource, ArticleData
from  xadmin import  views

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

class ArticleDataAdmin(object):
    list_display = ['title', 'original_source_name', 'publish_time']
    list_filter = ['original_source_name', 'title', 'location', 'type']
    style_fields = {"text": "ueditor"}

xadmin.site.register(ArticleSource, ArticleSourceAdmin)
xadmin.site.register(ArticleData, ArticleDataAdmin)
xadmin.site.register(views.CommAdminView, CommonXadminSettings)
xadmin.site.register(views.BaseAdminView, BaseXadminSettings)