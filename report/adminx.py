import xadmin
from .models import Content


class ContentAdmin(object):
    list_display = ('id','title', 'content', 'imgs', 'publish_time', 'view_count', 'is_put_top')

xadmin.site.register(Content, ContentAdmin)