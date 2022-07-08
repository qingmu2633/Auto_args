import hashlib
import json

from myenum.dao.enum_operation import into_sync_data, into_sync_record, query_sync_record_byID
from myenum.dao.ms_operation import query_args


def get_request_args(requestData):
    """
    根据接口定义请求解析请求里的所有参数
    """
    dic_obj = {}
    # print('解析接口名称为：'+requestData['name'])
    # json请求体解析
    if requestData['body']['kV'] and requestData['body']['valid']:
        for kvs in requestData['body']['kvs']:
            kv_list = []
            if kvs['valid'] and kvs['enable']:
                kv_list.append('kv')    # 加入标识
                if 'description' in kvs:
                    kv_list.append(kvs['description'])
                if 'max' in kvs:
                    kv_list.append(kvs['max'])
                if 'min' in kvs:
                    kv_list.append(kvs['min'])
                dic_obj.update({kvs['name']: kv_list})

    elif requestData['body']['json']:
        if 'format' in requestData['body'] and requestData['body']['format'] == 'JSON-SCHEMA':
            if 'properties' in requestData['body']['jsonSchema']:
                jsonSchema = requestData['body']['jsonSchema']['properties']
                # print('=========================')
                # print(jsonSchema)
                for k, v in jsonSchema.items():
                    # print(v)
                    j_list = []
                    j_list.append('jsonSchema')   # 加入标识
                    if 'description' in v:
                        j_list.append(v['description'])
                    if 'maxLength' in v:
                        j_list.append(v['maxLength'])
                    if 'minLength' in v:
                        j_list.append(v['minLength'])
                    # if 'default' in v:
                    #     j_list.append(v['default'])
                    # if 'enum' in v:
                    #     j_list.append(v['enum'])
                    # if 'format' in v:
                    #     j_list.append(v['format'])
                    dic_obj.update({k: j_list})
        elif 'raw' in requestData['body']:
            raw = requestData['body']['raw']
            jdata = json.loads(raw)
            for k, v in jdata.items():
                dic_obj.update({k: ['json']})

    # rest请求体
    if 'rest' in requestData:
        for rest in requestData['rest']:
            rest_list = []
            if rest['valid'] and rest['enable']:
                rest_list.append('rest')
                if 'description' in rest:
                    rest_list.append(rest['description'])
                if 'max' in rest:
                    rest_list.append(rest['max'])
                if 'min' in rest:
                    rest_list.append(rest['min'])
                dic_obj.update({rest['name']: rest_list})

    #query 请求体
    if 'arguments' in requestData:
        for arguments in requestData['arguments']:
            arg_list = []
            if arguments['valid'] and arguments['enable']:
                # print(arguments)
                arg_list.append('arguments')
                if 'description' in arguments:
                    arg_list.append(arguments['description'])
                if 'max' in arguments:
                    arg_list.append(arguments['max'])
                if 'min' in arguments:
                    arg_list.append(arguments['min'])
                dic_obj.update({arguments['name']: arg_list})

    # print(dic_obj)
    return dic_obj



def get_all_args(projectID):
    """
    根据项目ID一次性抽取所有请求的参数
    """
    resdata = query_args(projectID)
    n = 0
    list_args_data = []
    for m in range(len(resdata)):
        reqData = json.loads(resdata[m]['request'])
        # print(reqData['name'])
        dic_obj = get_request_args(reqData)
        # print(dic_obj)
        for k, v in dic_obj.items():
            list_args_data.append([])
            list_args_data[n].append(k)
            list_args_data[n].append(resdata[m]['api_name'])
            list_args_data[n].append(resdata[m]['path'])
            list_args_data[n].append(resdata[m]['project_name'])
            descp = '参数描述：'
            if len(v) > 3:
                descp += str(v[1]) + '; 最大长度：' + str(v[2]) + '; 最小长度：' + str(v[3])
            if len(v) == 3:
                descp += str(v[1]) + '; 最大长度：' + str(v[2])
            if len(v) == 2:
                descp += str(v[1])
            list_args_data[n].append(descp)
            list_args_data[n].append(resdata[m]['method'])

            n += 1
        #print('======================')
        # print(list_args_data)
    return list_args_data


def compareMD5(pid):
    # 获取之前文件md5
    befdata = query_sync_record_byID(pid)
    if befdata:
        # 查询所有参数，插入参数枚举表
        all_args_data = get_all_args(pid)
        # print('all_args_data ' + str(all_args_data))
        save_dic = {}
        for i in range(len(all_args_data)):
            if all_args_data[i][2] in save_dic:
                save_dic[all_args_data[i][2]].append(all_args_data[i])
            else:
                save_dic[all_args_data[i][2]] = [all_args_data[i]]

        # print('save_dic ' + str(save_dic))
        # 生成对应的md5
        aftmd5 = hashlib.md5(str(save_dic).encode('utf8')).hexdigest()
        if aftmd5 == befdata[0]['api_md5']:
            return "项目接口定义未发生变化无需同步"
        else:
            #前后md5有变化，则判断变化的部分
            bef_dic = json.loads(befdata[0]['api_definition'])
            bef_key = bef_dic.keys()
            aft_key = save_dic.keys()
            D = set(aft_key).difference(set(bef_key))  # 差集，在list2中但不在list1中的元素
            if D:
                add_list = []
                for val in all_args_data:
                    for v in D:
                        if v in val:
                            add_list.append(val)
                # print(add_list)
                # 插入枚举参数
                into_sync_data(add_list)

                # 更新后的接口定义信息写入数据库
                sync_list = []
                sync_list.append(all_args_data[0][3])
                sync_list.append(pid)
                sync_list.append(json.dumps(save_dic, ensure_ascii=False))
                sync_list.append(aftmd5)
                # 数据库记录
                into_sync_record(sync_list)
                return len(add_list)
            else:
                add_list = []
                for k, v in save_dic.items():  # 新的接口定义
                    if k in bef_dic:
                        bef_args = [val[0] for val in bef_dic[k]]  # 原来的的接口名称对应的字段集
                        aft_args = [val[0] for val in v]  # 所有新的接口名的字段集
                        # print(bef_args)
                        # print(aft_args)
                        #只处理新增的参数名称，不处理删除的参数
                        dif2 = set(aft_args).difference(set(bef_args))  # 差集，在list2中但不在list1中的元素
                        # print(dif2)
                        if dif2:  # 接口新增字段
                            for args in dif2:
                                for j in range(len(v)):
                                    if args in v[j][0]:
                                        add_list.append(v[j])

                # 插入枚举参数
                # print('add_list ' + str(add_list))
                into_sync_data(add_list)
                # 更新后的接口定义信息写入数据库
                sync_list = []
                sync_list.append(all_args_data[0][3])
                sync_list.append(pid)
                sync_list.append(json.dumps(save_dic, ensure_ascii=False))
                sync_list.append(aftmd5)
                # 数据库记录
                into_sync_record(sync_list)
                return len(add_list)


    # 若不存在之间的同步记录
    else:
        # 查询所有参数，插入参数枚举表
        all_args_data = get_all_args(pid)
        into_sync_data(all_args_data)

        save_dic = {}
        for i in range(len(all_args_data)):
            if all_args_data[i][2] in save_dic:
                save_dic[all_args_data[i][2]].append(all_args_data[i])
            else:
                save_dic[all_args_data[i][2]] = [all_args_data[i]]
        # 生成对应的md5
        aftmd5 = hashlib.md5(str(save_dic).encode('utf8')).hexdigest()

        # 记录同步==更新后的接口定义信息写入数据库
        sync_list = []
        sync_list.append(all_args_data[0][3])
        sync_list.append(pid)
        sync_list.append(json.dumps(save_dic, ensure_ascii=False))
        sync_list.append(aftmd5)
        # 数据库记录
        into_sync_record(sync_list)
        return len(all_args_data)






if __name__ == '__main__':
    pid = "3d142ad6-c0d5-492c-9fb2-360970a99bb5";

    projectID = "f60d98f4-e9aa-4176-a4fd-1e6bafd759ea"
    # get_all_args2(pid)
    befmd5 = compareMD5(pid)

    # print(type(befmd5))
    print(befmd5)
    # print(befmd5[0]['api_md5'])

    # num = 11
    # print(type(num))
    # if type(num) == type(0):
    #     print('2222')
    # # creat_case(projectID, "制度收藏")