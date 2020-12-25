from django.shortcuts import render
from django.http import JsonResponse,HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import os
from  PlagueDataImport.update_data import is_problem_data, get_need_update_day, update_global_data, update_region_data, add_US_recovered, add_other_country_recovered

import logging
import json
import pymysql
# Create your views here.

@csrf_exempt
def data_import(request):
    if request.method == 'POST':
        data_file = request.FILES.get('my_file', None)
        # data_file = request.FILES.getlist("my_file")
        if not data_file:
            return HttpResponse("<script>alert('没有文件上传');window.location.href='http://cms.emergevent.com/';</script>")
        if not data_file.name.endswith(".json"):
            return HttpResponse("<script>alert('上传文件格式错误');window.location.href='http://cms.emergevent.com/';</script>")
        print(data_file)
        try:
            # file_dir = "media/plague_data"
            # linux
            file_dir = "/project/PlagueAbroad/media/plague_data"
            if not os.path.exists(file_dir):
                os.mkdir(file_dir)
            with open(os.path.join(file_dir, "all.json"), 'wb+') as f:
                for chunk in data_file.chunks():
                    f.write(chunk)
            # linux
            fr = open("/project/PlagueAbroad/media/plague_data/all.json", "r", encoding="utf8")
            # fr = open(r"D:\Github\PlagueAbroad\media\plague_data\all.json", "r", encoding="utf8")
            data = json.load(fr)

            log_file = open("/project/PlagueAbroad/update.log", encoding="utf-8", mode="a")
            logging.basicConfig(level=logging.INFO, stream=log_file,
                                format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

            db = pymysql.connect(
                host="localhost",
                user="root",
                password="123456",
                database="covid_2019",
                charset="utf8"
            )

            cursor = db.cursor()

            need_update_day_list = get_need_update_day(data, cursor)

            # if is_problem_data(data):
            # 更新全球数据
            update_global_data(data, db, cursor, need_update_day_list)
            # 更新地区数据（包括添加新增的地区信息）
            update_region_data(data, db, cursor, need_update_day_list)

            # 更新美国的治愈数（因为要打开新的网页，可能存在更新不成功导致和前面的不同步的情况）
            add_US_recovered(cursor)

            r_country_list = ['Spain', 'Canada', 'Germany']
            add_other_country_recovered(cursor, r_country_list)

            cursor.close()
            db.close()
            logging.info("全球数据和地区数据更新成功----导入")
        except:
            return HttpResponse("<script>alert('解析出错');window.location.href='http://cms.emergevent.com/';</script>")

    return  HttpResponse("<script>alert('导入成功');window.location.href='http://cms.emergevent.com/';</script>")
    # return HttpResponseRedirect("http://127.0.0.1:8000/")