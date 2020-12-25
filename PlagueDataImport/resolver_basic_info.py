import json
import pymysql
from datetime import datetime
import requests

# 获取国家一级数据
def get_country_basic_info(data, cursor):
    region_id = 1
    region_parent_id = 0
    #插入所有国家
    for country_chinese, country_data in data.items():
        # print(country_chinese)
        # print(country_data)
        if country_chinese in ["全球", "confirmedCount", "deadCount", "curedCount"]:
            continue
        region_chinese = country_chinese
        region = country_data["ENGLISH"]
        region_level = 1
        sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                values("%d", "%s", "%s", "%d", "%d")''' % (region_id, region, region_chinese, region_parent_id, region_level)
        cursor.execute(sql)
        region_id += 1
        # if len(country_data) > 4:
        #     print(region_chinese)
        # break
    db.commit()
    return region_id

# 获取州、省二级数据
def get_province_basic_info(data, cursor):
    # 184个国家，使用185开头
    # region_id = 185

    select_sql = "select count(*) from region_basic_info"
    cursor.execute(select_sql)
    region_id = cursor.fetchone()[0]
    region_id += 1
    for country_chinese, country_data in data.items():
        if len(country_data) > 4:
            get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % country_chinese
            cursor.execute(get_region_parent_id_sql)
            region_parent_id = cursor.fetchone()[0]
            # print(region_parent_id)
            for province_chinese, province_data in country_data.items():
                # print(province_chinese)
                if province_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                    continue
                else:
                    if province_chinese == "中国大陆":
                        for cn_chinese, cn_data in province_data.items():
                            if cn_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                                continue
                            region_chinese = cn_chinese
                            region = cn_data["ENGLISH"]
                            region_level = 2
                            sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                                values("%d", "%s", "%s", "%d", "%d")''' % (region_id, region, region_chinese, region_parent_id, region_level)
                            cursor.execute(sql)
                            region_id += 1
                    else:
                        region_chinese = province_chinese
                        region = province_data["ENGLISH"]
                        region_level = 2
                        sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                                values("%d", "%s", "%s", "%d", "%d")''' % (region_id, region, region_chinese, region_parent_id, region_level)
                        cursor.execute(sql)
                        region_id += 1
        else:
            continue
    db.commit()

# 获取市三级数据
def get_city_basic_info(data, cursor):
    # 1123个国家和省/州，使用1124开头
    # region_id = 1124
    select_sql = "select count(*) from region_basic_info"
    cursor.execute(select_sql)
    region_id = cursor.fetchone()[0]
    region_id += 1
    for country_chinese, country_data in data.items():
        if len(country_data) > 4:
            for province_chinese, province_data in country_data.items():
                # 进入到省级
                if province_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                    continue
                # 中国大陆比较特殊，和在dict中和国家同级，因此需要先进入下一级
                if province_chinese == "中国大陆":
                    for cn_chinese, cn_data in province_data.items():
                        if cn_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                            continue
                        if len(cn_data) > 4:
                            get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % cn_chinese
                            cursor.execute(get_region_parent_id_sql)
                            region_parent_id = cursor.fetchone()[0]
                            print(region_parent_id)
                            for city_chinese, city_data in cn_data.items():
                                if city_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                                    continue
                                else:
                                    region_chinese = city_chinese
                                    if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data["ENGLISH"]:
                                        region = city_data["ENGLISH"][1:-1]
                                    else:
                                        region = city_data["ENGLISH"]
                                    region_level = 3
                                    sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                                            values("%d", "%s", "%s", "%d", "%d")''' % (region_id, region, region_chinese, region_parent_id, region_level)
                                    cursor.execute(sql)
                                    region_id += 1
                                    # print(region_chinese)
                else:
                    if len(province_data) > 4:
                        # print(province_chinese)
                        get_region_parent_id_sql = '''select id from region_basic_info where region_chinese = "%s"''' % province_chinese
                        cursor.execute(get_region_parent_id_sql)
                        region_parent_id = cursor.fetchone()[0]
                        print(region_parent_id)
                        
                        for city_chinese, city_data in province_data.items():
                            if city_chinese in ["ENGLISH", "confirmedCount", "deadCount", "curedCount"]:
                                continue
                            else:
                                region_chinese = city_chinese
                                if "Shihezi, Xinjiang Production and Construction Corps 8th Division" in city_data["ENGLISH"]:
                                    region = city_data["ENGLISH"][1:-1]
                                else:
                                    region = city_data["ENGLISH"]
                                region_level = 3
                                sql = '''insert into region_basic_info(id, region, region_chinese, region_parent_id, region_level) 
                                        values("%d", "%s", "%s", "%d", "%d")''' % (region_id, region, region_chinese, region_parent_id, region_level)
                                cursor.execute(sql)
                                region_id += 1
                                # print(region_chinese)
        else:
            continue
    db.commit()

if __name__ == "__main__":

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    }

    req = requests.get("https://raw.githubusercontent.com/stevenliuyi/covid19/master/public/data/all.json", headers = headers, verify=False)
    req.encoding = 'utf-8'
    fw = open("all.json", 'w', encoding='utf-8')
    json.dump(req.json(), fw, ensure_ascii=False, indent=4)
    fw.close()
    
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

    # 调用获取国家基本信息
    get_country_basic_info(data, cursor)

    # 调用获取州、省二级数据
    get_province_basic_info(data, cursor)

    # 调用获取市三级数据
    get_city_basic_info(data, cursor)

    cursor.close()
    db.close()
