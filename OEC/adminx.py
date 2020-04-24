import sqlalchemy
import pymysql
import xadmin
import pandas as pd

from .models import OECInfo

class OECInfoAdmin(object):
    list_display = ['region', 'name', 'related_info', 'type']
    list_filter = ['region', 'name', 'related_info', 'type']

    import_csv = True

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            file = request.FILES.get('excel')
            data_df = pd.read_csv(file, encoding='utf-8')
            sources = []
            idxs = OECInfo.objects.all().values('id')
            idxs_d = dict([(d['id'], True) for d in idxs])
            for index, item in data_df.iterrows():
                case = OECInfo()
                case.id = item.get('id')
                case.region = item.get('region')
                case.name = item.get('name')
                case.related_info = item.get('related_info')
                if item.get('type') == "驻外使馆":
                    case.type = 0
                elif item.get('type') == "驻外总领馆":
                    case.type = 1
                else:
                    case.type = 2
                if case.id not in idxs_d:
                    sources.append(case)
            if sources:
                OECInfo.objects.bulk_create(sources)

        return super(OECInfoAdmin, self).post(request, args, kwargs)

xadmin.site.register(OECInfo, OECInfoAdmin)
