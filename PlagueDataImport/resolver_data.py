import json
import pymysql
import pandas as pd
import datetime
from sqlalchemy import create_engine


# 获取全球数据
def get_global(data, cursor):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    '''
    # print(data["全球"])
    global_data = data["全球"]
    confirmed_dict = global_data["confirmedCount"]
    deaths_dict = global_data["deadCount"]
    recovered_dict = global_data["curedCount"]
    print(confirmed_dict.keys())
    # 确诊数的keys()肯定包含了死亡数和治愈数的keys()  ["2020-01-22", ...]
    for day_date in confirmed_dict.keys():
        confirmed = confirmed_dict[day_date]
        deaths = deaths_dict[day_date]
        recovered = recovered_dict[day_date]
        # print(str(confirmed) + "," + str(deaths) + "," + str(recovered))

        updated_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # sql = '''insert into global(confirmed, deaths, recovered, day_date, update_time)
        #         values("%d", "%d", "%d", "%s", "%s")''' % (confirmed, deaths, recovered, day_date, updated_time)
        sql = '''insert into global(confirmed, deaths, recovered, day_date, update_time)
                select "%d", "%d", "%d", "%s", "%s"
                where not exists(select 1 from global b where b.day_date = "%s")
            ''' % (confirmed, deaths, recovered, day_date, updated_time, day_date)
        cursor.execute(sql)
    db.commit()


# 将地区疫情数据存入DataFrame，便于转为csv以及写入数据库
def get_region_data2df(data, db, cursor, count, timelines):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    count：第一个写入数据库数据的id索引
    timelines：日期序列 ["2020-01-22", ...]
    '''
    # 保存DataFrame每列的数据
    id_list = []
    region_list = []
    confirmed_list = []
    deaths_list = []
    recovered_list = []
    day_date_list = []
    last_updated_list = []

    for country_chinese, country_data in data.items():
        # 国家级
        if country_chinese in ["全球", "confirmedCount", "deadCount", "curedCount"]:
            continue
        confirmed_dict = country_data["confirmedCount"]
        deaths_dict = country_data["deadCount"]
        recovered_dict = country_data["curedCount"]
        for day_date in timelines:
            # 若没有数据则为-1
            confirmed = -1
            deaths = -1
            recovered = -1
            if len(confirmed_dict) > 0:
                confirmed = 0
            if len(deaths_dict) > 0:
                deaths = 0
            if len(recovered_dict) > 0:
                recovered = 0
            if day_date in confirmed_dict:
                confirmed = confirmed_dict[day_date]
            if day_date in deaths_dict:
                deaths = deaths_dict[day_date]
            if day_date in recovered_dict:
                recovered = recovered_dict[day_date]
            print(count)

            last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            id_list.append(count)
            region_parent_id = 0
            # 拼接region，用于唯一区分一条数据，便于找到父级id
            region = country_chinese + "_" + country_data['ENGLISH'] + "_" + str(region_parent_id)
            region_list.append(region)
            confirmed_list.append(confirmed)
            deaths_list.append(deaths)
            recovered_list.append(recovered)
            day_date_list.append(day_date)
            last_updated_list.append(last_updated)
            print(str(confirmed) + "," + str(deaths) + "," + str(recovered))
            count += 1
        # 当键的个数大于4个时，表示存在下一级区域。 不存在下一级区域的只包括ENGLISH、confirmedCount、deadCount、curedCount这4个键
        if len(country_data) > 4:
            # 进入到省级
            for province_chinese, province_data in country_data.items():
                if province_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                    continue
                # print(province_chinese)
                # 中国大陆比较特殊，和在dict中和国家同级，因此需要先进入下一级（我们不保存中国大陆的总数据，仅保存里面包含的各个省的数据）
                if province_chinese == "中国大陆":
                    for cn_chinese, cn_data in province_data.items():
                        if cn_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                            continue

                        # 先插入省级数据
                        # 获取国级（父级）的id
                        get_pro_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % "中国"
                        cursor.execute(get_pro_region_parent_id_sql)
                        pro_region_parent_id = cursor.fetchone()[0]
                        pro_region_e = cn_data["ENGLISH"]
                        confirmed_dict = cn_data["confirmedCount"]
                        deaths_dict = cn_data["deadCount"]
                        recovered_dict = cn_data["curedCount"]
                        for day_date in timelines:
                            confirmed = -1
                            deaths = -1
                            recovered = -1
                            if len(confirmed_dict) > 0:
                                confirmed = 0
                            if len(deaths_dict) > 0:
                                deaths = 0
                            if len(recovered_dict) > 0:
                                recovered = 0
                            if day_date in confirmed_dict:
                                confirmed = confirmed_dict[day_date]
                            if day_date in deaths_dict:
                                deaths = deaths_dict[day_date]
                            if day_date in recovered_dict:
                                recovered = recovered_dict[day_date]
                            print(count)
                            last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            id_list.append(count)
                            # region_list.append(country_chinese)
                            region = cn_chinese + "_" + pro_region_e + "_" + str(pro_region_parent_id)
                            region_list.append(region)
                            confirmed_list.append(confirmed)
                            deaths_list.append(deaths)
                            recovered_list.append(recovered)
                            day_date_list.append(day_date)
                            last_updated_list.append(last_updated)
                            print(str(confirmed) + "," + str(deaths) + "," + str(recovered))
                            count += 1

                        # 省中的键的个数大于4，则表示存在市级
                        if len(cn_data) > 4:
                            # 获取省级（父级）的id
                            get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % cn_chinese
                            cursor.execute(get_region_parent_id_sql)
                            region_parent_id = cursor.fetchone()[0]

                            # 遍历省包含的数据，即市级数据
                            for city_chinese, city_data in cn_data.items():
                                if city_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                                    continue

                                # 源数据json中有一个格式错误的地方，特殊处理
                                if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data[
                                    "ENGLISH"]:
                                    region_e = city_data["ENGLISH"][1:-1]
                                else:
                                    region_e = city_data["ENGLISH"]
                                confirmed_dict = city_data["confirmedCount"]
                                deaths_dict = city_data["deadCount"]
                                recovered_dict = city_data["curedCount"]
                                for day_date in timelines:
                                    confirmed = -1
                                    deaths = -1
                                    recovered = -1
                                    if len(confirmed_dict) > 0:
                                        confirmed = 0
                                    if len(deaths_dict) > 0:
                                        deaths = 0
                                    if len(recovered_dict) > 0:
                                        recovered = 0
                                    if day_date in confirmed_dict:
                                        confirmed = confirmed_dict[day_date]
                                    if day_date in deaths_dict:
                                        deaths = deaths_dict[day_date]
                                    if day_date in recovered_dict:
                                        recovered = recovered_dict[day_date]
                                    print(count)
                                    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    id_list.append(count)
                                    # region_list.append(country_chinese)
                                    region = city_chinese + "_" + region_e + "_" + str(region_parent_id)
                                    region_list.append(region)
                                    confirmed_list.append(confirmed)
                                    deaths_list.append(deaths)
                                    recovered_list.append(recovered)
                                    day_date_list.append(day_date)
                                    last_updated_list.append(last_updated)
                                    print(str(confirmed) + "," + str(deaths) + "," + str(recovered))
                                    count += 1
                                    # print(region_chinese)
                    continue
                # else:
                #     if province_chinese in ["香港", "台湾", "澳门", "海外领土"]:
                #         get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % country_chinese
                #         cursor.execute(get_region_parent_id_sql)
                #         region_parent_id = cursor.fetchone()[0]

                # 获取父级(国家级)的id
                get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % country_chinese
                print(country_chinese)
                cursor.execute(get_region_parent_id_sql)

                # 当出现新的国家并且包含省份数据时，此时这个国家还没有添加到region_basic_info表中，导致出错 20200807
                parent_id_result = cursor.fetchone()
                if parent_id_result != None:
                    region_parent_id = parent_id_result[0]
                else:
                    # 若该国家数据不存在，则直接插入region_basic_info先
                    select_sql = "select count(*) from region_basic_info"
                    cursor.execute(select_sql)
                    total = cursor.fetchone()[0]
                    insert_region_id = total + 1
                    insert_country_sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                        values("%d", "%s", "%s", "%d", "%d")''' % (
                    insert_region_id, country_data['ENGLISH'], country_chinese, 0, 1)
                    cursor.execute(insert_country_sql)
                    db.commit()
                    region_parent_id = insert_region_id
                # print("region_parent_id:", region_parent_id)
                confirmed_dict = province_data["confirmedCount"]
                deaths_dict = province_data["deadCount"]
                recovered_dict = province_data["curedCount"]
                for day_date in timelines:
                    confirmed = -1
                    deaths = -1
                    recovered = -1
                    if len(confirmed_dict) > 0:
                        confirmed = 0
                    if len(deaths_dict) > 0:
                        deaths = 0
                    if len(recovered_dict) > 0:
                        recovered = 0
                    if day_date in confirmed_dict:
                        confirmed = confirmed_dict[day_date]
                    if day_date in deaths_dict:
                        deaths = deaths_dict[day_date]
                    if day_date in recovered_dict:
                        recovered = recovered_dict[day_date]
                    print(count)
                    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(province_chinese)
                    if province_chinese == 'undefined':
                        continue
                    region = province_chinese + "_" + province_data['ENGLISH'] + "_" + str(region_parent_id)
                    id_list.append(count)
                    region_list.append(region)
                    # region_list.append(country_chinese)
                    confirmed_list.append(confirmed)
                    deaths_list.append(deaths)
                    recovered_list.append(recovered)
                    day_date_list.append(day_date)
                    last_updated_list.append(last_updated)
                    print(str(confirmed) + "," + str(deaths) + "," + str(recovered))
                    count += 1
                # 进入到省/州级
                if len(province_data) > 4:
                    get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % province_chinese
                    print(province_chinese)
                    cursor.execute(get_region_parent_id_sql)
                    # region_parent_id = cursor.fetchone()[0]
                    region_parent_id_c = cursor.fetchone()

                    # 当出现新的国家存在省州级数据时，会出现id查不到的问题（希腊），暂时直接pass
                    if region_parent_id_c is None:
                        continue
                    else:
                        region_parent_id = region_parent_id_c[0]

                    # print(province_chinese)
                    for city_chinese, city_data in province_data.items():
                        if city_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                            continue
                        else:
                            if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data[
                                "ENGLISH"]:
                                region_e = city_data["ENGLISH"][1:-1]
                            else:
                                region_e = city_data["ENGLISH"]
                            confirmed_dict = city_data["confirmedCount"]
                            deaths_dict = city_data["deadCount"]
                            recovered_dict = city_data["curedCount"]
                            for day_date in timelines:
                                confirmed = -1
                                deaths = -1
                                recovered = -1
                                if len(confirmed_dict) > 0:
                                    confirmed = 0
                                if len(deaths_dict) > 0:
                                    deaths = 0
                                if len(recovered_dict) > 0:
                                    recovered = 0
                                if day_date in confirmed_dict:
                                    confirmed = confirmed_dict[day_date]
                                if day_date in deaths_dict:
                                    deaths = deaths_dict[day_date]
                                if day_date in recovered_dict:
                                    recovered = recovered_dict[day_date]
                                print(count)
                                last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                id_list.append(count)
                                # region_list.append(country_chinese)
                                region = city_chinese + "_" + region_e + "_" + str(region_parent_id)
                                region_list.append(region)
                                confirmed_list.append(confirmed)
                                deaths_list.append(deaths)
                                recovered_list.append(recovered)
                                day_date_list.append(day_date)
                                last_updated_list.append(last_updated)
                                print(str(confirmed) + "," + str(deaths) + "," + str(recovered))
                                count += 1
    # 将列表转换为字典，便于构建DataFrame
    region_data_dict = {
        'id': id_list,
        'region': region_list,
        'confirmed': confirmed_list,
        'deaths': deaths_list,
        'recovered': recovered_list,
        'day_date': day_date_list,
        'last_updated': last_updated_list
    }
    region_data_df = pd.DataFrame(data=region_data_dict,
                                  columns=['id', 'region', 'confirmed', 'deaths', 'recovered', 'day_date',
                                           'last_updated'])

    return region_data_df


# 将获取的DataFrame的地区疫情数据存入csv
def get_region_data2csv(data, cursor):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    '''
    db_index = 1
    region_data_df = get_region_data2df(data, cursor, db_index, data["全球"]["confirmedCount"])
    region_data_df.to_csv('region_data.csv', index=0)  # 不保存行索引


# 构建region和id的字典
def build_region_dict(cursor):
    sql = "select id, region, region_chinese, region_parent_id from region_basic_info"
    cursor.execute(sql)
    datas = cursor.fetchall()
    region_dict = {}
    for r_data in datas:
        value = r_data[0]
        if r_data[3] != None:
            key = r_data[2] + '_' + r_data[1] + "_" + str(r_data[3])
        else:
            key = r_data[2] + '_' + r_data[1]
        region_dict[key] = value
    region_json = json.dumps(region_dict, ensure_ascii=False, indent=4)
    f = open("region_name2id.json", 'w', encoding='utf-8')
    f.write(region_json)
    # json.dump(region_json, f, ensure_ascii = False, indent=4)
    f.close()


# 将地区疫情数据存入数据库（通过读取csv文件中的数据）
def get_region_data():
    r_data = pd.read_csv("region_data.csv")
    region_list = list(r_data['region'])
    f = open('region_name2id.json', 'r', encoding="utf-8")
    region_dict = json.load(f)
    # print(region_dict.items())

    # 将region列置换为数据库中region对应的id列
    region_id_list = []
    for region in region_list:
        region_id = region_dict[region]
        # print(region_id)
        region_id_list.append(region_id)
    r_data['region_id'] = region_id_list

    r_data = r_data.drop('region', axis=1)
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/covid_2019?charset=utf8')
    con = engine.connect()
    r_data.to_sql("region_data", con, if_exists='append', index=False)
    # print(r_data)
    # print(region_list)


# 补全美国的治愈数
def add_US_all_recovered(cursor):
    try:
        base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
        # 更新所有美国的治愈数据（从4月12号开始）
        # https://raw.githubusercontent.com/CSSEGISandData/COVID-19上从4月12号开始有治愈数据
        begin_time = datetime.datetime(2020, 5, 14)
        total_delta = (datetime.datetime.now() - begin_time).days
        print(total_delta)
        for delta in range(0, total_delta):
            add_delta = datetime.timedelta(delta)
            url_day_date_str = (datetime.datetime.date(begin_time) + add_delta).strftime("%m-%d-%Y")
            print(url_day_date_str)

            url = base_url + url_day_date_str + '.csv'
            us_data = pd.read_csv(url)
            # print(us_data)

            day_date_str = (datetime.datetime.date(begin_time) + add_delta).strftime("%Y-%m-%d")
            # 获取美国的州名称列表
            state_name = list(us_data[:]["Province_State"])

            for region in state_name:
                # 根据州名称转换为id
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
                        # 对于NaN的数据赋值为0
                        recovered_d = 0
                    print(recovered_d)
                    # 更新数据
                    sql = "update region_data set recovered = %d where region_id = %d and day_date = '%s'" % (
                    recovered_d, region_id, day_date_str)
                    cursor.execute(sql)

            db.commit()
    except Exception:
        print("csv不存在或网络异常")


# 补全其他国家的治愈数
def add_other_country_all_recovered(cursor, country_name):
    try:
        base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
        # 更新该国家所有的治愈数据（从3月22号开始）
        # https://raw.githubusercontent.com/CSSEGISandData/COVID-19上从3月22号开始有治愈数据，西班牙、加拿大和德国都是5月14开始
        begin_time = datetime.datetime(2020, 5, 14)
        total_delta = (datetime.datetime.now() - begin_time).days
        print("total_delta:", total_delta)
        for delta in range(0, total_delta):
            add_delta = datetime.timedelta(delta)
            url_day_date_str = (datetime.datetime.date(begin_time) + add_delta).strftime("%m-%d-%Y")
            print(url_day_date_str)

            url = base_url + url_day_date_str + '.csv'
            print(url)
            country_data = pd.read_csv(url)
            # print(country_data)

            day_date_str = (datetime.datetime.date(begin_time) + add_delta).strftime("%Y-%m-%d")
            # 获取该国家的州名称列表
            state_name = list(country_data.loc[country_data["Country_Region"] == country_name, "Province_State"])
            print("state_name:", state_name)

            for region in state_name:
                # 根据州名称转换为id
                sql = "select id from region_basic_info where region = '%s'" % region
                cursor.execute(sql)
                result = cursor.fetchone()
                if result != None:
                    region_id = result[0]
                    # print(region)
                    # print(region_id)
                    try:
                        recovered_d = int(country_data.loc[country_data["Province_State"] == region, "Recovered"])
                    except Exception:
                        # 对于NaN的数据赋值为0
                        recovered_d = 0
                    print(recovered_d)
                    # 更新数据
                    sql = "update region_data set recovered = %d where region_id = %d and day_date = '%s'" % (
                    recovered_d, region_id, day_date_str)
                    cursor.execute(sql)

            db.commit()
    except Exception:
        print("csv不存在或网络异常")


if __name__ == "__main__":
    # f = open('all_20200509.json', 'r', encoding="utf-8")
    # data = json.load(f)

    db = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="covid_2019",
        charset="utf8"
    )

    cursor = db.cursor()
    # 调用获取全球数据
    # get_global(data, cursor)

    # # 将地区疫情数据转入csv文件
    # get_region_data2csv(data, cursor)

    # # 构建region和id的字典
    # build_region_dict(cursor)

    # # 获取地区疫情数据，存入数据库
    # get_region_data()

    # 补全美国的治愈数
    # add_US_all_recovered(cursor)

    add_other_country_all_recovered(cursor, "Spain")
    add_other_country_all_recovered(cursor, "Canada")
    add_other_country_all_recovered(cursor, "Germany")

    cursor.close()
    db.close()