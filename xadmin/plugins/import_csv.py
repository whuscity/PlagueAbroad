import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict


#excel 导入
class ListImportCSVPlugin(BaseAdminPlugin):
    import_csv = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_csv)

    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/csv/tooolbar_importcsv.html', context=get_context_dict(context)))


xadmin.site.register_plugin(ListImportCSVPlugin, ListAdminView)