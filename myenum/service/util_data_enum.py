import json

from myenum.dao import enum_operation
# from myenum.dao.enum_operation import query_sync_record_byName


# 获取接口定义中的项目名称，接口名称，接口url
def get_api_name_list(args_name):
    project_obj = enum_operation.query_sync_record_byName()
    # print(project_obj)
    # api_name_list = []
    pro_dic = {}
    for data in project_obj:
        api_def_obj = json.loads(data['api_definition'])
        # print(api_def_obj)
        for k, v in api_def_obj.items():
            for i in range(len(v)):
                if v[i][0] == args_name:
                    # api_name_list.append({'project_name': v[i][3], 'args_name': v[i][1], 'api_url': v[i][2]})
                    if v[i][3] in pro_dic:
                        if v[i][1] and v[i][1] not in pro_dic[v[i][3]]:  # 去重
                            pro_dic[v[i][3]].append({'api_name': v[i][1], 'api_url': v[i][2], 'mark': v[i][4]})
                    else:
                        if v[i][3]:
                            pro_dic[v[i][3]] = [{'api_name': v[i][1], 'api_url': v[i][2], 'mark': v[i][4]}]

    # print(api_name_list)
    # print('11111111111111111111111111')
    # print(pro_dic)
    return pro_dic


# 根据项目，接口及参数获取对应的参数枚举值正反例
def get_enum_data(argsList, api_name, project_name):
    d = enum_operation.getEnumData(argsList)
    # print(d)
    dic_T1, dic_T2, dic_T3 = {}, {}, {}
    dic_F1, dic_F2, dic_F3 = {}, {}, {}
    for data in d:
        # 未指定公用的
        if data['args_api'] == '0':
            if data['args_status'] == '正例':
                if data['args_name'] in dic_T1:
                    if data['args_value'] not in dic_T1[data['args_name']]:
                        dic_T1[data['args_name']].append(data['args_value'])
                else:
                    dic_T1[data['args_name']] = [data['args_value']]

            if data['args_status'] == '反例':
                if data['args_name'] in dic_F1:
                    if data['args_value'] not in dic_F1[data['args_name']]:
                        dic_F1[data['args_name']].append(data['args_value'])
                else:
                    dic_F1[data['args_name']] = [data['args_value']]

    for data in d:
        # 指定了项目的
        if data['args_api'] == '1' and data['project_name'] == project_name and data['api_name'] is None:
            if data['args_status'] == '正例':
                if data['args_name'] in dic_T2:
                    if data['args_value'] not in dic_T2[data['args_name']]:
                        dic_T2[data['args_name']].append(data['args_value'])
                else:
                    dic_T2[data['args_name']] = [data['args_value']]

            if data['args_status'] == '反例':
                if data['args_name'] in dic_F2:
                    if data['args_value'] not in dic_F2[data['args_name']]:
                        dic_F2[data['args_name']].append(data['args_value'])
                else:
                    dic_F2[data['args_name']] = [data['args_value']]

    for data in d:
        # 指定了项目和接口的
        if data['args_api'] == '1' and data['project_name'] == project_name and data['api_name'] == api_name:
            if data['args_status'] == '正例':
                if data['args_name'] in dic_T3:
                    if data['args_value'] not in dic_T3[data['args_name']]:
                        dic_T3[data['args_name']].append(data['args_value'])
                else:
                    dic_T3[data['args_name']] = [data['args_value']]

            if data['args_status'] == '反例':
                if data['args_name'] in dic_F3:
                    if data['args_value'] not in dic_F3[data['args_name']]:
                        dic_F3[data['args_name']].append(data['args_value'])
                else:
                    dic_F3[data['args_name']] = [data['args_value']]

    dic_T, dic_F = {}, {}
    dic_T.update(dic_T1)
    dic_T.update(dic_T2)
    dic_T.update(dic_T3)
    dic_F.update(dic_F1)
    dic_F.update(dic_F2)
    dic_F.update(dic_F3)

    re_list = []

    # print('--------------')
    # print(dic_T)
    # print(dic_F)
    # print('--------------')

    re_list.append(dic_T)
    re_list.append(dic_F)
    print('正反例参数为： ' + str(re_list))
    return re_list


if __name__ == '__main__':
    print(get_api_name_list('name'))