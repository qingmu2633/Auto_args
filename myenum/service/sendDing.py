import hashlib
import json
from datetime import datetime

import requests
from django.template.defaultfilters import upper

from myenum.dao.enum_operation import query_cron_job, query_sync_record_byID, into_sync_record, into_sync_data
from myenum.dao.ms_operation import query_swagger_url, query_by_sql, delete_api_by_url, query_project
from myenum.service.args_sync import get_all_args


def dingTalk(content, weburl):
    content = {
        "msgtype": "text",
        "text": {
            "content": content  # 这里必须包含之前定义关键字
        },
        "at": {
            # 发送给群里的所有人
            "isAtAll": True
            # 单独 @ 某个人，使用绑定的手机号，
            # 多个人用户英文逗号隔开
            # "131xxxxxx811",
            # "137xxxxxxxxx"
        }
    }
    headers = {"Content-Type": "application/json;charset=utf-8"}
    # 绿金技术群
    # url = "https://oapi.dingtalk.com/robot/send?access_token=958337e36af091dca873737721429802e45515e5509777cf5214a3e000507b2f"
    # demo
    # url = "https://oapi.dingtalk.com/robot/send?access_token=7edc63dfeee39a083a07b32f3baa0e3fbeb20354e1319c84607b89ed48d79d58"
    r = requests.post(url=weburl, headers=headers, json=content)
    print(r.content.decode())


def find_sameorDiff_Number(list1, list2):
    # A = set(list1).intersection(set(list2)) #交集
    # B = set(list1).union(set(list2)) # 并集
    C = set(list1).difference(set(list2)) #差集，在list1中但不在list2中的元素
    D = set(list2).difference(set(list1)) #差集，在list2中但不在list1中的元素
    # print("交集元素个数:" +str(len(A)))
    # print("并集元素个数:" +str(len(B)))
    # print("在list1中但不在list2中的元素个数:" +str(len(C)))
    # print("在list2中但不在list1中的元素个数:" +str(len(D)))
    return C, D


def getDiffer(project_id, webhook):
    pname = query_project()
    for val in pname:
        if val['id'] == project_id:
            contents = val['name'] + ' -> 接口更新消息通知：\n'
    if not contents:
        contents = ' 接口更新消息通知：\n'

    #获取之前接口定义信息
    befdata = query_sync_record_byID(project_id)
    # print(befdata[0]['api_definition'])
    list_args_data = get_all_args(project_id)    # 当前的接口定义信息
    # list_args_data = get_all_args('652794a3-e368-44a8-ba09-cf03831c22aa')    # 当前的接口定义信息

    if not list_args_data:
        print('当前的接口定义查询无信息，请检查ms平台接口定时同步是否正常！')
        return

    # 0401 修改以url为接口是否重复判断依据
    save_dic = {}
    # print(list_args_data)
    for i in range(len(list_args_data)):
        if list_args_data[i][2] in save_dic:
            save_dic[list_args_data[i][2]].append(list_args_data[i])
        else:
            save_dic[list_args_data[i][2]] = [list_args_data[i]]

    # print(json.dumps(save_dic, ensure_ascii=False))
    #生成md5
    aftmd5 = hashlib.md5(str(save_dic).encode('utf8')).hexdigest()
    #
    if befdata and aftmd5 == befdata[0]['api_md5']:
        d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(d + ' 当前项目id为：'+project_id+' -----文件md5码相同-----')
        return
    else:
        add_list = []   # 有差异的枚举参数
        # 比对不一致的地方
        if befdata:
            str_to_dict = json.loads(befdata[0]['api_definition'])
            # print(str_to_dict)
        else:
            str_to_dict = {}
        # print(type(str_to_dict))

        bef_key = str_to_dict.keys()
        aft_key = save_dic.keys()
        bef_dif, aft_dif = find_sameorDiff_Number(bef_key, aft_key)

        if bef_dif:
            for addvalue in bef_dif:
                contents += '删除了接口： ' + str_to_dict[addvalue][0][1] +' -> '+ addvalue + '\n'
                print('删除了接口： ' + str_to_dict[addvalue][0][1] +' -> '+ addvalue)

        if aft_dif:
            for delvalue in aft_dif:
                contents += '新增了接口： ' + save_dic[delvalue][0][1] +' -> '+ delvalue + '\n'
                print('新增了接口： ' + save_dic[delvalue][0][1] +' -> '+ delvalue)

            # 如果参数有新增，则收集新增数据（只处理新增的接口，不处理删除的接口）
            for val in list_args_data:
                for v in aft_dif:
                    if v in val:
                        add_list.append(val)

        # print(str_to_dict)
        for k, v in save_dic.items():  #新的接口定义
            if k in str_to_dict:     # 新的url 在原有的定义中存在
                if v[0][1] != str_to_dict[k][0][1]:
                    contents += '接口：' + v[0][1] +' -> ' + k + ' 更新了名称 -> 更新前：' + str_to_dict[k][0][1] + ' <--> 更新后：' + v[0][1] + '\n'
                    print('接口：' + v[0][1] +' -> ' + k + ' 更新了名称 -> 更新前：' + str_to_dict[k][0][1] + ' <--> 更新后：' + v[0][1])

                if v[0][5] != str_to_dict[k][0][5]:
                    contents += '接口：' + v[0][1] + ' -> ' + k + ' 更新了请求方式 -> 更新前：' + str_to_dict[k][0][5] + ' <--> 更新后：' + v[0][5] + '\n'
                    print('接口：' + v[0][1] + ' -> ' + k + ' 更新了请求方式 -> 更新前：' + str_to_dict[k][0][5] + ' <--> 更新后：' + v[0][5])

                bef_args = [val[0] for val in str_to_dict[k]]   # 原来的的接口名称对应的字段集
                aft_args = [val[0] for val in v]    # 所有新的接口名的字段集
                dif1, dif2 = find_sameorDiff_Number(bef_args, aft_args)
                if dif1:  # 接口删除字段
                    for args in dif1:
                        contents += '接口：' + v[0][1]+' -> '+ k + ' 删除了字段: ' + args + '\n'
                        print('接口：'+v[0][1]+' -> '+k+' 删除了字段: '+args)
                if dif2:   # 接口新增字段
                    for args in dif2:
                        contents += '接口：' + v[0][1]+' -> '+k + ' 新增了字段: ' + args + '\n'
                        print('接口：' + v[0][1]+' -> '+k + ' 新增了字段: ' + args)

                        # 只处理新增的参数名称，不处理删除的参数
                        for j in range(len(v)):
                            if args in v[j][0]:
                                add_list.append(v[j])

                for m in range(len(v)):
                    for n in range(len(str_to_dict[k])):
                        if v[m][0] == str_to_dict[k][n][0] and v[m][5] == str_to_dict[k][n][5]:    # 参数相同时,且请求方式相同
                            if v[m][4] != str_to_dict[k][n][4]:
                                contents += '接口：' + v[m][1] +' -> ' + k + ' 字段：' + v[m][0] + ' 更新了描述 -> 更新前：' + str_to_dict[k][n][4] + ' <--> 更新后：' + v[m][4] + '\n'
                                print('接口：' + v[m][1] +' -> ' + k + ' 字段：' + v[m][0] + ' 更新了描述 -> 更新前：' + str_to_dict[k][n][4] + ' <--> 更新后：' + v[m][4])


        # # 插入枚举参数
        # print('add_list ' + str(add_list))
        if add_list:
            into_sync_data(add_list)

        # 更新后的接口定义信息写入数据库
        sync_list = []
        sync_list.append(list_args_data[0][3])
        sync_list.append(project_id)
        sync_list.append(json.dumps(save_dic, ensure_ascii=False))
        sync_list.append(aftmd5)
        # 数据库记录
        into_sync_record(sync_list)

    # 有变化发送钉钉消息
    if not (contents[-10:-2] == '接口更新消息通知'):
        # print(str(len(contents)))
        defalut_num = 15000
        if len(contents) > defalut_num:
            str_length = len(contents) // defalut_num
            # print(str_length)
            for i in range(str_length):
                # print(contents[i*defalut_num: i*defalut_num+defalut_num])
                # print('---------------')
                dingTalk('接口更新消息通知：\n'+contents[i*defalut_num: i*defalut_num+defalut_num], webhook)
            # print(contents[str_length*defalut_num: len(contents)])
            dingTalk('接口更新消息通知：\n'+contents[str_length*defalut_num: len(contents)], webhook)
        else:
            # print(contents)
            dingTalk(contents, webhook)


def excute_cron():
    obj_cron = query_cron_job()
    for data in obj_cron:
        # print(data['project_id'])
        # print(data['webhook'])
        msg = del_ms_api(data['project_id'])   # 更新先删除接口
        if msg:
            dingTalk('接口更新消息通知：\n'+msg, data['webhook'])
        getDiffer(data['project_id'], data['webhook'])


# TODO：处理swagger同步后删除的url，等版本升级后有该功能了可以注释掉
def del_ms_api(project_id):
    # print(data['project_id'])
    swagger_url = query_swagger_url(project_id)
    # swagger_url = [{'swagger_url': 'http://10.1.1.114:8001/myenum/static/test2.json'}]
    update_api = []   # 存放url
    update_method = []
    flag = True
    for url in swagger_url:
        r = requests.get(url['swagger_url'])   # 读取swagger_url
        # print(r.status_code)
        if r.status_code == 200:
            # print(r.json()['basePath'])
            basePath = r.json()['basePath']
            for k, v in r.json()['paths'].items():
                temp = {}
                if basePath == '/':
                    path = k
                else:
                    path = basePath + k
                update_api.append(path)
                for m, n in v.items():
                    temp.update({path: m})
                    update_method.append(temp)
        else:
            flag = False
            print('当前swagger_url读取失败：'+url['swagger_url'])
            data_msg = '当前swagger_url读取失败：' + url['swagger_url']
            return data_msg

    if flag:
        # print(update_api)
        # print(update_method)
        # 查询ms中接口定义的数据
        api_data = query_by_sql(project_id, '')
        # print(api_data)
        for api_url in api_data:
            # 0426 确实有相同url但不同方式的存在的
            # for val in update_method:
            #     for k, v in val.items():
            #         if api_url['path'] == k and upper(v) != api_url['method']:
            #             # delete_api_by_url(api_url['path'], api_url['method'])
            #             print('-----删除了url1: ' + api_url['path']+ ' - ' +k+' - ' + v +' - ' + api_url['method'])

            if api_url['path'] not in update_api:
                print('-----删除了url2: ' + api_url['path'])
                delete_api_by_url(api_url['path'], api_url['method'])


if __name__ == '__main__':
    # obj_cron = query_cron_job()
    # for data in obj_cron:
    #     print(data['project_id'])
    # #     # print(data['webhook'])
    #     ttttt(data['project_id'])
    #     del_ms_api(data['project_id'])
    #     getDiffer(data['project_id'], data['webhook'])
    # del_ms_api('652794a3-e368-44a8-ba09-cf03831c22aa')
    # getDiffer('3d142ad6-c0d5-492c-9fb2-360970a99bb5', 'webhook')   # demo项目
    # getDiffer('652794a3-e368-44a8-ba09-cf03831c22bb', 'webhook')
    # getDiffer('652794a3-e368-44a8-ba09-cf03831c22aa', 'webhook')    # 绿色金融
    # del_ms_api('7a20ccaa-3c65-432c-9a30-807c24360183')  # 更新先删除接口
    # getDiffer('7a20ccaa-3c65-432c-9a30-807c24360183', 'webhook')    # 名单服务
    excute_cron()
    # ttttt('652794a3-e368-44a8-ba09-cf03831c22aa')
    print('1111')

