import sqlalchemy
import pymysql
import xadmin
import pandas as pd

from .models import OECInfo

class OECInfoAdmin(object):
    list_display = ['region', 'name', 'address', 'phone', 'url', 'email', 'type']
    list_filter = ['region', 'name','address', 'phone', 'url', 'email', 'type']

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
                case.name = item.get('name')
                case.region = item.get('region')
                case.related_info = item.get('related_info')
                case.address = item.get('address')
                case.url = item.get('url')
                case.phone = item.get('phone')
                case.email = item.get('email')
                # if str(item.get('region')) == 'nan':
                #     case.region = None
                # if str(item.get('name')) != 'nan':
                #     case.name = None
                # if str(item.get('related_info')) != 'nan':
                #     case.related_info = None
                # if str(item.get('address')) != 'nan':
                #     case.address = None
                # if str(item.get('url')) != 'nan':
                #     case.url = None
                # if str(item.get('phone')) != 'nan':
                #     case.phone = None
                # if str(item.get('email')) != 'nan':
                #     case.email = None

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
