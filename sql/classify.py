from sql.sql_tools import pg_tools

db = pg_tools()

provinces = ['北京', '天津', '上海', '重庆', '黑龙江', '吉林', '辽宁', '河北', '河南', '山东', '江苏', '浙江', '福建',
             '广东', '广西', '云南', '海南', '西藏', '新疆', '内蒙古', '青海', '宁夏', '甘肃', '陕西', '山西',
             '四川', '贵州', '湖南', '湖北', '江西', '安徽', '香港', '澳门', '台湾']


def classify_location():
    rows = db.select("select weibo_id, content,timestamp from weibo_item where type = '肺炎疫情,政策'")
    print(len(rows))
    for item in rows:
        for province in provinces:
            if province in item[1]:
                db.insert("insert into local_policy(weibo_id, location, timestamp) "
                          "values ('{weibo_id}', '{location}', '{timestamp}')".format(weibo_id=item[0],
                                                                                      location=province,
                                                                                      timestamp=item[2]))


if __name__ == '__main__':
    classify_location()
