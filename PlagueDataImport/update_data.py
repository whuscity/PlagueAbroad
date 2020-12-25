import json
import pymysql
import datetime
import pandas as pd
from sqlalchemy import create_engine
import requests

from . import resolver_data
import logging

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
    if delta >= 0:
        # 包括前一天的日期
        for day in range(0, delta + 1):
        # 不包括前一天的日期
        # for day in range(1, delta + 1):
            add_delta = datetime.timedelta(days = day)
            need_update_day = last_day_date + add_delta
            need_update_day_str = datetime.datetime.strftime(need_update_day, "%Y-%m-%d")
            need_update_day_list.append(need_update_day_str)
    print(need_update_day_list)

    # 获取今天的日期，不更新当天的数据
    today_date = datetime.datetime.now().date()
    today_date_str = today_date.strftime("%Y-%m-%d")
    print(today_date_str)
    if today_date_str in need_update_day_list:
        need_update_day_list.remove(today_date_str)

    return need_update_day_list

# 全球数据更新
def update_global_data(data, db, cursor, need_update_day_list):
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
            sql = '''update global set confirmed = "%d", deaths = "%d", recovered = "%d", update_time = "%s"
                     where day_date = "%s"''' % (confirmed, deaths, recovered, update_time, day_date)
        cursor.execute(sql)

    db.commit()

# 更新地区数据（包括添加新增的地区信息,新增的地区信息仅包含need_update_day_list列表中包含的日期数据）
def update_region_data(data, db, cursor, need_update_day_list):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    need_update_day_list：需要更新的日期列表  格式是["2020-04-22", "2020-04-23",...]
    '''

    # 更新之前重新生成字典，防止出错
    resolver_data.build_region_dict(cursor)

    # 获取region_data表中当前最后一条数据的id
    select_sql = "select count(*) from region_data"
    cursor.execute(select_sql)
    # 传入索引
    db_index = cursor.fetchone()[0] + 1
    
    # 获取新增的region_data的DataFrame格式的数据
    region_data_df = resolver_data.get_region_data2df(data, db, cursor, db_index, need_update_day_list)

    # 当有新的国家数据插入时，需要重新生成 20200807
    resolver_data.build_region_dict(cursor)

    # print(region_data_df)
    # 将DataFrame格式的数据的region列存入list，格式为["阿富汗_Afghanistan", "拉潘帕省_La Pampa_7"]
            # region列数据由三个字段拼接而成：region_chinse,region,region_parent_id
            # 使用"_"分隔
            # 用于唯一标识一条数据
    df_region_list = list(region_data_df['region'])

    # 获取region行和id对应的字典 {"阿富汗_Afghanistan": 1,"阿尔巴尼亚_Albania": 2,...}
    # linux
    f = open('/project/PlagueAbroad/EpidemicInfo/region_name2id.json', 'r', encoding="utf-8")
    # f = open(r'region_name2id.json', 'r', encoding="utf-8")
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
                    # 2020.05.01 确实出现了新的国家，绝望...

                    # 获取父级的region_level值
                    region_parent_id = int(new_region_info[2])

                    # 判断是否为国家
                    if region_parent_id == 0:
                        region_level = 1
                    else:
                        parent_sql = "select region_level from region_basic_info where id = '%d'" % region_parent_id
                        cursor.execute(parent_sql)
                        parent_region_level = cursor.fetchone()[0]
                        # 当前地区的region_level即为父级加1
                        region_level = parent_region_level + 1

                    if region not in region_dict:
                        # 将新的地区数据插入到region_basic_info表
                        sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level)
                            values("%d", "%s", "%s", "%d", "%d")''' % (current_region_id, region_name, region_chinese, region_parent_id, region_level)
                        cursor.execute(sql)
                    # 若存在则不插入
                    # sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level)
                    #     select "%d", "%s", "%s", "%d", "%d"
                    #     where not exists(select 1 from region_basic_info b
                    #     where b.region = "%s" and b.region_chinese = "%s" and b.region_parent_id = "%d")
                    #     ''' % (current_region_id, region_name, region_chinese, region_parent_id, region_level, region_name, region_chinese, region_parent_id)
                    # print(sql)
                    # cursor.execute(sql)

                    # 保存当前插入的地区的id
                    save_current_region_id = current_region_id

                    region_id_list.append(current_region_id)
                    current_region_id += 1
                else:
                    # 没有上一级，则其本身就是国家级
                    region_level = 1
                    region_parent_id = 0

                    if region not in region_dict:
                        sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level)
                            values("%d", "%s", "%s", "%d", "%d")''' % (current_region_id, region_name, region_chinese, region_parent_id, region_level)
                        cursor.execute(sql)
                    # # 若存在则不插入
                    # sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level)
                    #     select "%d", "%s", "%s", "%d", "%d"
                    #     where not exists(select 1 from region_basic_info b
                    #     where b.region = "%s" and b.region_chinese = "%s" and b.region_parent_id = "%d")
                    #     ''' % (current_region_id, region_name, region_chinese, region_parent_id, region_level, region_name, region_chinese, region_parent_id)
                    # print(sql)
                    # cursor.execute(sql)

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
    
    # 法一：直接写入，将新增的region_data写入数据库
    # engine = create_engine('mysql+pymysql://root:123456@localhost:3306/covid_2019?charset=utf8')
    # con = engine.connect()
    # region_data_df.to_sql("region_data", con, if_exists = 'append', index = False)
    
    # 20200430更新，对新增的数据去重
    print(region_data_df)
    print(len(region_data_df))
    # 给region_data建一个字典 主要字段为region_id, day_date
    select_data_sql = "select id, region_id, day_date from region_data"
    cursor.execute(select_data_sql)
    all_data = cursor.fetchall()
    # print(all_data[:10])
    # 使用list速度也相对较慢，但比数据库判断是否重复要快
    # l = []
    region_data_dict = {}
    for d in all_data:
        data_id = d[0]
        region_id = d[1]
        day_date = d[2]
        # l.append(str(region_id) + "_" + day_date)
        # 随便赋一个值
        region_data_dict[str(region_id) + "_" + day_date] = data_id

    # 获取待更新治愈数地区的id列表
    r_region_id_list = get_recovered_region_id_list(cursor)

    # 更新数,更新的数据占用了id，因此需要减掉
    count = 0
    for index, row in region_data_df.iterrows():
        data_id = row['id'] - count
        region_id = row['region_id']
        confirmed = row['confirmed']
        deaths = row['deaths']
        recovered = row['recovered']
        day_date = row['day_date']
        last_updated = row['last_updated']

        rd_key = str(region_id) + "_" + day_date

        if rd_key not in region_data_dict:
            sql_insert_update = '''insert into region_data(id, region_id, confirmed, deaths, recovered, day_date, last_updated)
                                values("%d", "%d", "%d", "%d", "%d", "%s", "%s")
                            ''' % (data_id, region_id, confirmed, deaths, recovered, day_date, last_updated)
            cursor.execute(sql_insert_update)
        else:
            d_id = region_data_dict[rd_key]
            # print(d_id)
        #     # sql_insert_update = ''' update region_data set confirmed = "%d", deaths = "%d", recovered = "%d"
        #     #                     where region_id = "%d" and day_date = "%s"
        #     #                 ''' % (confirmed, deaths, recovered, region_id, day_date)
            # 建一个id索引，增加查询速度
            if d_id in r_region_id_list:
                # 判断是否是需要单独更新治愈数的地区，如果是，则更新全部数据的时候不更新治愈数
                sql_insert_update = ''' update region_data set confirmed = "%d", deaths = "%d", last_updated = "%s"
                                            where id = "%d"
                                        ''' % (confirmed, deaths, last_updated, d_id)
            else:
                sql_insert_update = ''' update region_data set confirmed = "%d", deaths = "%d", recovered = "%d", last_updated = "%s"
                                                where id = "%d"
                                            ''' % (confirmed, deaths, recovered, last_updated, d_id)
        # print(sql_insert_update)
            cursor.execute(sql_insert_update)
            count += 1
    db.commit()

    #     print(data_id, region_id, confirmed, deaths, recovered, day_date, last_updated)

    #     # 速度太慢了
    #     sql_insert_data = '''insert into region_data(id, region_id, confirmed, deaths, recovered, day_date, last_updated)
    #             select "%d", "%d", "%d", "%d", "%d", "%s", "%s"
    #             where not exists(select 1 from region_data b
    #             where b.day_date = "%s" and b.region_id = "%d")
    #         ''' % (data_id, region_id, confirmed, deaths, recovered, day_date, last_updated, day_date, region_id)
    #     # # if index % 100 == 0 or index == len(region_data_df) - 1:
    #     cursor.execute(sql_insert_data)
    # db.commit()
    
    # 更新完成之后需要重新生成字典
    resolver_data.build_region_dict(cursor)

# 通过最新的两条数据判断是否存在问题
# 20200628更新
def is_problem_data(data):
    global_data = data["全球"]
    confirmed_dict = global_data["confirmedCount"]
    deaths_dict = global_data["deadCount"]
    recovered_dict = global_data["curedCount"]

    all_dates = list(confirmed_dict.keys())

    # 获取今天的日期，不更新当天的数据
    today_date = datetime.datetime.now().date()
    today_date_str = today_date.strftime("%Y-%m-%d")

    if today_date_str in all_dates:
        logging.info("存在当天数据，但不更新")
        # return False
        day_1 = all_dates[-2]
        day_2 = all_dates[-3]
        print(day_1)
        print(day_2)
    else:
        # day_1 = need_update_day_list[-1]
        # day_2 = need_update_day_list[-2]
        day_1 = all_dates[-1]
        day_2 = all_dates[-2]
        print(day_1)
        print(day_2)

    confirmed_dif = confirmed_dict[day_1] - confirmed_dict[day_2]
    deaths_dif = deaths_dict[day_1] - deaths_dict[day_2]
    recovered_dif = recovered_dict[day_1] - recovered_dict[day_2]

    if confirmed_dif < 0 or deaths_dif < 0 or recovered_dif < 0 or (confirmed_dif == 0 and deaths_dif == 0 and recovered_dif == 0):
        return False
    else:
        return True

# 更新美国的治愈数
def add_US_recovered(cursor):
    try:
        base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
        for delta in range(2, 0, -1):
            # 更新前两天的数据
            add_delta = datetime.timedelta(-delta)
            url_day_date_str = (datetime.datetime.date(datetime.datetime.now()) + add_delta).strftime("%m-%d-%Y")
            print(url_day_date_str, type(url_day_date_str))
            url = base_url + url_day_date_str + '.csv'
            us_data = pd.read_csv(url)
            # print(us_data)

            day_date_str = (datetime.datetime.date(datetime.datetime.now()) + add_delta).strftime("%Y-%m-%d")
            state_name = list(us_data[:]["Province_State"])

            for region in state_name:
                sql = "select id from region_basic_info where region = '%s'" % region
                cursor.execute(sql)
                result = cursor.fetchone()
                if result != None:
                    region_id = result[0]
                    # print(region)
                    # print(region_id)
                    try:
                        recovered_d = int(us_data.loc[us_data["Province_State"] == region, "Recovered"])
                    except Exception:
                        recovered_d = 0
                    print(recovered_d)
                    sql = "update region_data set recovered = %d where region_id = %d and day_date = '%s'" % (recovered_d, region_id, day_date_str)
                    cursor.execute(sql)

            db.commit()
            logging.info("US " + url_day_date_str + "治愈数更新成功")
    except Exception:
        logging.info("US csv不存在或网络异常")


def add_other_country_recovered(cursor, r_country_list):
    try:
        # https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/05-31-2020.csv
        base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
        # 更新前两天的数据
        for delta in range(2, 0, -1):
            add_delta = datetime.timedelta(-delta)
            url_day_date_str = (datetime.datetime.date(datetime.datetime.now()) + add_delta).strftime("%m-%d-%Y")
            print(url_day_date_str, type(url_day_date_str))
            url = base_url + url_day_date_str + '.csv'
            print(url)
            country_data = pd.read_csv(url)
            # print(us_data)

            day_date_str = (datetime.datetime.date(datetime.datetime.now()) + add_delta).strftime("%Y-%m-%d")
            for country_name in r_country_list:
                state_name = list(country_data.loc[country_data["Country_Region"] == country_name, "Province_State"])

                # print(state_name)

                for region in state_name:
                    sql = "select id from region_basic_info where region = '%s'" % region
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if result != None:
                        region_id = result[0]
                        # print(region)
                        # print("region_id:", region_id)
                        try:
                            recovered_d = int(country_data.loc[country_data["Province_State"] == region, "Recovered"])
                        except Exception:
                            recovered_d = 0
                        # print(recovered_d)
                        sql = "update region_data set recovered = %d where region_id = %d and day_date = '%s'" % (
                        recovered_d, region_id, day_date_str)
                        cursor.execute(sql)

                db.commit()
                logging.info(country_name + " " + url_day_date_str + "治愈数更新成功")
    except Exception:
        logging.info("Other Country csv不存在或网络异常")


def get_recovered_region_id_list(cursor):
    # 20200603更新，给定治愈数更新的国家列表
    r_country_list = ['Spain', 'Canada', 'Germany', 'United States of America']
    r_region_id_list = []
    for r_country in r_country_list:
        # 获取国家id
        region_parent_id_sql = "select id from region_basic_info where region = '%s'" % r_country
        cursor.execute(region_parent_id_sql)
        r_region_country_id = cursor.fetchone()[0]

        # 获取国家下面州或省的id列表
        region_ids_sql = "select id from region_basic_info where region_parent_id = %d" % r_region_country_id
        cursor.execute(region_ids_sql)
        region_ids = cursor.fetchall()
        region_ids_list = [r_id[0] for r_id in region_ids]

        r_region_id_list += region_ids_list

    return r_region_id_list

if __name__ == "__main__":

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }

    req = requests.get("https://raw.githubusercontent.com/stevenliuyi/covid19/master/public/data/all.json" ,headers = headers)
    req.encoding = 'utf-8'

    #linux
    fw = open("/project/PlagueAbroad/EpidemicInfo/all.json", 'w', encoding='utf-8')
    # fw = open(r"all.json", 'w', encoding='utf-8')
    json.dump(req.json(), fw, ensure_ascii=False, indent=4)
    fw.close()

    #linux
    fr = open("/project/PlagueAbroad/EpidemicInfo/all.json", "r", encoding="utf8")
    # fr = open(r"all.json", "r", encoding="utf8")
    data = json.load(fr)

    log_file = open("update.log", encoding="utf-8", mode="a")
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

    if is_problem_data(data):

        # 更新全球数据
        update_global_data(data, cursor, need_update_day_list)
        # 更新地区数据（包括添加新增的地区信息）
        update_region_data(data, db, cursor, need_update_day_list)

        # 更新美国的治愈数（因为要打开新的网页，可能存在更新不成功导致和前面的不同步的情况）
        add_US_recovered(cursor)

        r_country_list = ['Spain', 'Canada', 'Germany']
        add_other_country_recovered(cursor, r_country_list)

        cursor.close()
        db.close()
        logging.info("全球数据和地区数据更新成功")
    else:
        logging.info("存在脏数据")

