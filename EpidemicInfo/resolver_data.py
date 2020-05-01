import json
import pymysql
import pandas as pd
import datetime
from sqlalchemy import create_engine

#获取全球数据
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
def get_region_data2df(data, cursor, count, timelines):
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
                                if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data["ENGLISH"]:
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
                cursor.execute(get_region_parent_id_sql)
                region_parent_id = cursor.fetchone()[0]
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
                    id_list.append(count)
                    region = province_chinese + "_" + province_data['ENGLISH'] + "_" + str(region_parent_id)
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
                    cursor.execute(get_region_parent_id_sql)
                    region_parent_id = cursor.fetchone()[0]

                    # print(province_chinese)
                    for city_chinese, city_data in province_data.items():
                        if city_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                            continue
                        else:
                            if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data["ENGLISH"]:
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
    region_data_df = pd.DataFrame(data = region_data_dict, columns=['id', 'region', 'confirmed', 'deaths', 'recovered', 'day_date', 'last_updated'])

    return region_data_df

# 将获取的DataFrame的地区疫情数据存入csv
def get_region_data2csv(data, cursor):
    '''
    data：json格式的所有的数据
    cursor：数据库cursor
    '''
    db_index = 1
    region_data_df = get_region_data2df(data, cursor, db_index, data["全球"]["confirmedCount"])
    region_data_df.to_csv('region_data.csv',index=0) #不保存行索引

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
    region_json = json.dumps(region_dict, ensure_ascii = False, indent=4)
    # linux
    f = open("/project/PlagueAbroad/EpidemicInfo/region_name2id.json", 'w', encoding='utf-8')
    # f = open("region_name2id.json", 'w', encoding = 'utf-8')
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
    r_data.to_sql("region_data", con, if_exists = 'append', index = False)
    # print(r_data)
    # print(region_list)

if __name__ == "__main__":

    f = open('all.json', 'r', encoding="utf-8")
    data = json.load(f)

    db = pymysql.connect(
        host = "localhost",
        user = "root",
        password = "123456",
        database = "covid_2019",
        charset = "utf8"
    )

    cursor = db.cursor()
    # 调用获取全球数据
    get_global(data, cursor)

    # 将地区疫情数据转入csv文件
    get_region_data2csv(data, cursor)

    # 构建region和id的字典
    build_region_dict(cursor)

    # 获取地区疫情数据，存入数据库
    get_region_data()

    cursor.close()
    db.close()