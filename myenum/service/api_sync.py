import hashlib
import json

import requests

from myenum.dao.enum_operation import query_cron_job, into_test_sync_record, query_test_sync_record_byID
from myenum.dao.ms_operation import query_swagger_url


def get_api_data():
    # print('11111111')
    # swagger_url = query_swagger_url(project_id)
    pro_data = query_cron_job()
    for p_id in pro_data:
        # print(p_id)
        print(p_id['project_id'])
        swagger_url = query_swagger_url(p_id['project_id'])
        for s_url in swagger_url:
            print(s_url['swagger_url'])
            # url = 'http://swagger-greenfinance.abchina-zj-dev.hsjdata.com/v2/api-docs?group=%E5%86%9C%E8%A1%8C%E7%BB%BF%E9%87%91'
            resp = requests.get(s_url['swagger_url'])
            print(resp.status_code)
            if resp.status_code == 200:
                # query_test_sync_record_byID(p_id['project_id'])
                # 生成md5
                aftmd5 = hashlib.md5(str(resp.text).encode('utf8')).hexdigest()
                # 更新后的接口定义信息写入数据库
                sync_list = []
                sync_list.append('test')
                sync_list.append(p_id['project_id'])
                sync_list.append(resp.text)
                sync_list.append(aftmd5)
                # 数据库记录
                into_test_sync_record(sync_list)

if __name__ == '__main__':
    get_api_data()
    url = 'http://swagger-greenfinance.abchina-zj-dev.hsjdata.com/v2/api-docs?group=农行绿金'
    resp = requests.get(url)
    print(resp.status_code)
    print(resp.text)

