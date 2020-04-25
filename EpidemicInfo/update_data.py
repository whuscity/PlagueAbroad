import json
import pymysql
import datetime
import pandas as pd
from sqlalchemy import create_engine
import requests

from . import resolver_data

# 根据全球的时间序列获取数据库中需要更新的疫情日期
def get_need_update_day(data, cursor):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor

    return：需要更新的疫情日期列表 ["2020-04-23",...]
    '''
    global_data = data["全球"]
    confirmed_dict = global_data["confirmedCount"]

    # 获取数据库中当前数据的最新日期
    sql = "select id, max(day_date)  FROM global WHERE day_date = (SELECT max(day_date) FROM global)"
    cursor.execute(sql)
    result = cursor.fetchone()
    last_day_id = result[0]
    last_day_date = result[1]
    # date转为字符串，再转为datetime
    # last_day_date = datetime.strptime(datetime.strftime(result[1], "%Y-%m-%d"), "%Y-%m-%d")

    # print(last_day_id)
    # print(type(last_day_date))
    # print(last_day_date)


    # 获取新获取的json文件中当前数据的最新日期
    confirmed_dict_keys = list(confirmed_dict.keys())
    json_last_day_date_str = confirmed_dict_keys[len(confirmed_dict_keys) - 1]
    json_last_day_date = datetime.datetime.strptime(json_last_day_date_str, "%Y-%m-%d").date()

    # 计算间隔的天数
    delta = (json_last_day_date - last_day_date).days
    print(delta)

    # 获取未更新数据的日期（如果可以包括前一天的日期，则防止数据未更新完毕或者出错的情况）
    need_update_day_list = []
    if delta >= 1:
        # for day in range(0, delta + 1):
        # 暂时不包括前一天的日期
        for day in range(1, delta + 1):
            add_delta = datetime.timedelta(days = day)
            need_update_day = last_day_date + add_delta
            need_update_day_str = datetime.datetime.strftime(need_update_day, "%Y-%m-%d")
            need_update_day_list.append(need_update_day_str)
    print(need_update_day_list)

    return need_update_day_list

# 全球数据更新
def update_global_data(data, cursor, need_update_day_list):
    global_data = data["全球"]
    confirmed_dict = global_data["confirmedCount"]
    deaths_dict = global_data["deadCount"]
    recovered_dict = global_data["curedCount"]
    
    for update_day in need_update_day_list:
        confirmed = confirmed_dict[update_day]
        deaths = deaths_dict[update_day]
        recovered = recovered_dict[update_day]
        day_date = update_day
        # print(datetime.datetime.now())
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(confirmed, deaths, recovered, update_time)

        select_sql = '''select id from global where day_date = "%s"''' % day_date
        cursor.execute(select_sql)
        update_day_id = cursor.fetchone()
        if update_day_id == None:
            sql = '''insert into global(confirmed, deaths, recovered, day_date, update_time) 
                    values('%d', '%d', '%d', '%s', '%s')''' % (confirmed, deaths, recovered, day_date, update_time)
        else:
            sql = '''update global set confirmed = "%d", deaths = "%d", recovered = "%d"
                     where day_date = "%s"''' % (confirmed, deaths, recovered, day_date)
        cursor.execute(sql)

    db.commit()

# 更新地区数据（包括添加新增的地区信息,新增的地区信息仅包含need_update_day_list列表中包含的日期数据）
def update_region_data(data, cursor, need_update_day_list):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    need_update_day_list：需要更新的日期列表  格式是["2020-04-22", "2020-04-23",...]
    '''
    # 获取region_data表中当前最后一条数据的id
    select_sql = "select count(*) from region_data"
    cursor.execute(select_sql)
    # 传入索引
    db_index = cursor.fetchone()[0] + 1
    
    # 获取新增的region_data的DataFrame格式的数据
    region_data_df = resolver_data.get_region_data2df(data, cursor, db_index, need_update_day_list)

    # print(region_data_df)
    # 将DataFrame格式的数据的region列存入list，格式为["阿富汗_Afghanistan", "拉潘帕省_La Pampa_7"]
            # region列数据由三个字段拼接而成：region_chinse,region,region_parent_id
            # 使用"_"分隔
            # 用于唯一标识一条数据
    df_region_list = list(region_data_df['region'])

    # 获取region行和id对应的字典 {"阿富汗_Afghanistan": 1,"阿尔巴尼亚_Albania": 2,...}
    f = open(r'D:\workspace\vscode_workspace\COVID19_Test\20200422\region_name2id.json', 'r', encoding="utf-8")
    region_dict = json.load(f)
    # print(region_dict.items())
    region_id_list = []

    # 获取region_basic_info中最后一条数据的id，便于新增地区的时候找到id
    select_sql = "select count(*) from region_basic_info"
    cursor.execute(select_sql)
    current_region_id = cursor.fetchone()[0] + 1
    # print("current_region_id:", current_region_id)

    # 保存新增的地区列表，用于去重（因为根据时间序列新增的df_region_list可能出现重复的region的现象，因为可能一下子同时更新n天的数据，这时候df_region_list就会出现n个重复的region）
    new_region_list = []
    # 更新地区信息，并将DataFrame中的region置换为对应的id
    for region in df_region_list:
        # 判断有没有新的地区出现,有则需要先添加地区信息
        if region in region_dict:
            region_id = region_dict[region]
            # print(region_id)
            region_id_list.append(region_id)
        else:
            # 新的地区，需要先添加到region_basic_info表

            #判断当前地区是否在新增地区中已插入数据库的列表里，用于去重
            if region not in new_region_list:
                # 解析region列数据
                new_region_info = region.split("_")
                # print(new_region_info)
                region_chinese = new_region_info[0]
                region_name = new_region_info[1]

                # 判断是否存在父级
                if len(new_region_info) > 2:
                    # 是否要判断新增的是国家级还是省级（感觉疫情发展到今天，应该是包括所有国家了），暂时先不判断

                    # 获取父级的region_level值
                    region_parent_id = int(new_region_info[2])
                    parent_sql = "select region_level from region_basic_info where id = '%d'" % region_parent_id
                    cursor.execute(parent_sql)
                    parent_region_level = cursor.fetchone()[0]
                    # 当前地区的region_level即为父级加1
                    region_level = parent_region_level + 1

                    # 将新的地区数据插入到region_basic_info表
                    sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level)
                        values("%d", "%s", "%s", "%d", "%d")''' % (current_region_id, region_name, region_chinese, region_parent_id, region_level)
                    # print(sql)
                    cursor.execute(sql)

                    # 保存当前插入的地区的id
                    save_current_region_id = current_region_id

                    region_id_list.append(current_region_id)
                    current_region_id += 1
                else:
                    # 没有上一级，则其本身就是国家级
                    region_level = 1
                    sql = '''insert into region_basic_info(id, region, region_chinese, region_level)
                        values("%d", "%s", "%s", "%d")''' % (current_region_id, region_name, region_chinese, region_level)
                    # print(sql)
                    cursor.execute(sql)

                    # 保存当前插入的地区的id
                    save_current_region_id = current_region_id

                    region_id_list.append(current_region_id)
                    current_region_id += 1

                # 将region添加到new_region_list列表中
                new_region_list.append(region)
            else:
                # 当存在重复时，仍然需要将新增地区的id添加，否则会导致list过短而报错
                region_id_list.append(save_current_region_id)
    db.commit()

    # 置换region为region_id
    region_data_df['region_id'] = region_id_list
    # print(region_data_df)
    region_data_df = region_data_df.drop('region', axis=1)
    # 将新增的region_data写入数据库
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/covid_2019?charset=utf8')
    con = engine.connect()
    region_data_df.to_sql("region_data", con, if_exists = 'append', index = False)
    
    # 更新完成之后需要重新生成字典
    resolver_data.build_region_dict(cursor)

if __name__ == "__main__":

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }

    req = requests.get("https://raw.githubusercontent.com/stevenliuyi/covid19/master/public/data/all.json" ,headers = headers)
    req.encoding = 'utf-8'
    fw = open(r"D:\Github\PlagueAbroad\EpidemicInfo\all.json", 'w', encoding='utf-8')
    json.dump(req.json(), fw, ensure_ascii=False, indent=4)
    fw.close()
    
    fr = open(r"D:\Github\PlagueAbroad\EpidemicInfo\all.json", "r", encoding="utf8")
    data = json.load(fr)

    db = pymysql.connect(
        host = "localhost",
        user = "root",
        password = "123456",
        database = "covid_2019",
        charset = "utf8"
    )

    cursor = db.cursor()

    need_update_day_list = get_need_update_day(data, cursor)
    # 更新全球数据
    update_global_data(data, cursor, need_update_day_list)
    # 更新地区数据（包括添加新增的地区信息）
    update_region_data(data, cursor, need_update_day_list)
