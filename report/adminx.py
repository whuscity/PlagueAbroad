import xadmin
from .models import Content


class ContentAdmin(object):
    list_display = ('id','title', 'wechat_url', 'publish_time', 'view_count', 'type', 'is_put_top')
    style_fields = {"content": "ueditor"}

xadmin.site.register(Content, ContentAdmin)