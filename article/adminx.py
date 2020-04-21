import xadmin
from .models import ArticleModel

class ArticleModelAdmin(object):
    list_display = ['title', 'origin_source_name', 'publish_time']
    list_filter = ['origin_source_name', 'title', 'location', 'type']
    style_fields = {"text": "ueditor"}

xadmin.site.register(ArticleModel, ArticleModelAdmin)
