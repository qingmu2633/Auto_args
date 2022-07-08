import copy
import itertools
import random
import json

from myenum.dao import enum_operation
from myenum.dao.ms_operation import ins_manay, query_by_sql, query_args
from myenum.service.util_data_enum import get_enum_data

final_count = 1000

def digui_sum(list_data):
    """
        根据接口参数的TF个数，计算生成case的总数
    """
    sum = 0   #除全正例之外的case总数
    tt = 1   #全正例T的总数
    len_all = len(list_data)
    for x in range(0, len_all):
        tt = tt * list_data[x][0]
        ttt = 1  #带有一个F组合的总数
        tempc = len_all - 1 - x
        for y in range(0, len_all):
            if y != tempc:
                ttt = ttt * list_data[y][0]
            else:
                ttt = ttt * list_data[tempc][1]
        #print(ttt)
        sum += ttt
        # print(list1[len(list1)-1-x][1])
    total = sum+tt   #case总数
    # print(total)
    if total > 1000:
        #如果总数大于1000，则每个参数的T列表个数减一，直到总数小于1000
        for i in range(len_all):
            if list_data[i][0] > 1:
                list_data[i][0] -= 1
        #print(list_data)
        digui_sum(list_data)

    return list_data


# 获取参数枚举值组合用例
def getEnum(argsList, api_name,project_name):
    list_comb = []     #所有参数枚举值的组合

    leng = len(argsList)
    print(api_name +" --接口请求参数个数：" + str(leng)+"--"+str(argsList))
    if leng == 0:    # 当接口没有参数
        return list_comb, 1

    if leng > 30:
        print(api_name + " --接口请求参数个数：" + str(leng) + " 参数个数过长，请手动组合接口用例！")
        return list_comb, 1
    # 参数全部取出来 TODO 后续这里转换的都可以优化
    list_all = []   # 格式 [ {"key1": [{T},{F}]}, {"key2": [{T},{F}]}, {"key3": [{T},{F}]} ]
    entData = get_enum_data(argsList, api_name, project_name)
    # print(entData)
    keys = [k for k, v in entData[0].items()]   #查询数据返回的参数个数
    #print("枚举参数值"+str(keys))
    if leng > len(keys):
        print("=======1111111111111111111111111111111111111111111111111111=有请求参数没有枚举值======111111111111111111111111111111111111111111=====")
        return list_comb, 1

    ## 转换成 [ {"key1": [{T},{F}]}, {"key2": [{T},{F}]}, {"key3": [{T},{F}]} ]
    for n in argsList:
        dic = {}
        #if n in keys:    #如果请求中的参数在枚举里
        key = []
        key.append(set(entData[0][n]))      #T
        key.append(set(entData[1][n]))    #set去重，F
        dic.update({n: key})
        list_all.append(dic)

    #   name              #T           #F
    #[{'pageSize':[{'', '12', '}, {'', '-1', 'ggg'}]},
    # {'pageNum': [{'7777', '2'}, {'-1', 'sadsdasd'}]},
    # {'entInfo': [{'兴业证券股份有限公司'}, {'5555', '213'}]}]
    # print("list_all===所有参数枚举值==="+str(list_all))


    #当只有一个参数的时候
    if leng == 1:
        list_1 = [list(v[0])+list(v[1]) for k, v in list_all[0].items()]
        # 计算T的长度
        len_t = [len(v[0]) for v in list_all[0].values()]
        print('当前接口只有一个参数，参数枚举值为：' + str(list_1[0]) + ' 正例长度为：' + str(len_t[0]))
        return list_1[0], len_t[0]

    # =========================
    # 获取每个参数的T的长度，F的长度
    # [[9, 7], [17, 15], [1, 2]]
    len_all_list = []
    for x in range(len(list_all)):
        len_all_list.append([])
        for k, v in list_all[x].items():
            len_all_list[x].append(len(v[0]))
            len_all_list[x].append(len(v[1]))

    len_all_list_temp = copy.deepcopy(len_all_list)  #深拷贝
    digui_sum(len_all_list)   #递归调用使其case总数小于1000
    # print('==============================')
    # 如果总数大于1000，走了递归的
    if len_all_list_temp != len_all_list:
        limit_len = [x[0] for x in len_all_list]
        # print(limit_len)
        for i in range(0, len(list_all)):
            for k, v in list_all[i].items():
                if len(v[0]) > limit_len[i]:
                    #print(list_all[i].get(argsList[i])[0])
                    temp = random.sample(list_all[i].get(argsList[i])[0], limit_len[i])
                    #print(temp)
                    list_all[i].get(argsList[i])[0] = temp

        # print('缩减后的list_all为：'+str(list_all))

    #转化成 DTF 列表
    tempT, tempF = [], []
    for m in list_all:
        for k, v in m.items():
            tempT.append(v[0])  # T
            tempF.append(v[1])  # F
    # print("D: " + str(tempD))
    # print("T: " + str(tempT))
    # print("F: " + str(tempF))
    #    #pageSize               #pageNum                  #entInfo
    #T: [{'122', '13', '99'}, {'7777', '2', '12', '3'}, {'兴业证券股份有限公司'}]
    #F: [{'', '-1', 'ggg'}, {'-1','1', '0.0', '0', None}, {'5555', '213'}]
    # print('===========================================================\n')

    """ # TODO
         ## DTF排列组合生成方式,可随机调整组合生成方式
    """
    list_it = [tempT, tempF]
    res_list = itertools.product(list_it, repeat=leng)
    list_c = [n for n in res_list if n.count(tempF) < 2]  # 过滤掉有2个F以上的组合
    # list = [n for n in res_list if n.count(tempD) >=(leng-1)]  #组合加过滤条件，不加条件就是全组合

    ## 根据DTF组合，每个组合获取对应的枚举参数
    # list_DTF 2个参数的，TT，TF，； 3个参数就是TTT，TTF,TFT,FTT,
    # [
    #     [{'', '99', '11'}, {'99', '11', '3', '12'}, {'兴业证券股份有限公司', '321'}],  # TTT
    #     [{'', '99', '11'}, {'99', '11', '3', '12'}, {'213', '5555'}],  # TTF
    #     [{'', '99', '11'}, {'-1', 's', '0.0', '1', None}, {'兴业证券股份有限公司', '321'}],  # TFT
    #     [{'', 'ggg', '-1'}, {'99', '11', '3', '12'}, {'兴业证券股份有限公司', '321'}]  # FTT
    # ]
    list_DTF = []
    for mm in list_c:
        temp = []
        cc = 0
        for y in mm:
            temp.append(y[cc])
            cc += 1
        list_DTF.append(temp)
    # print("list_DTF is : "+str(list_DTF))

    # ===================================
    # 计算TT组合的个数
    sum = 1
    if list_DTF:
        list_T_len = [len(ml) for ml in list_DTF[0]]
        for x in list_T_len:
            sum = sum * x
    # print(sum)
    # ===================================

    ## 根究DTF组合生成具体参数组
    for m in list_DTF:
        res_list1 = itertools.product(*m)
        list2 = [n for n in res_list1]
        list_comb += list2
    # print(list_comb)
    # print('case排列组合总数为:', len(list_comb))

    return list_comb, sum


def analBody(requestData, project_name):
    """
        解析接口定义中的参数,123中可能同时存在, 3中只会存在一种
        1. query 参数
        2. rest 参数
        3. 请求体-form-data  x-www-form-urlencoded json  xml raw  binary
        参数解析后生成对应的枚举值
    """
    list_manay = []
    reqData = json.loads(requestData)
    # print(requestData)
    keyList = []
    len1, len2, len3 = 0, 0, 0
    if reqData['body']['kV'] and reqData['body']['valid']:
        # 获取所有的请求参数
        keyList1 = [data['name'] for data in reqData['body']['kvs'] if data['valid']]
        len1 = len(keyList1)
        keyList += keyList1
    elif reqData['body']['json']:
        if 'format' in reqData['body'] and reqData['body']['format'] == 'JSON-SCHEMA':
            if 'properties' in reqData['body']['jsonSchema']:
                jsonSchema = reqData['body']['jsonSchema']['properties']
                keyList1 = [k for k, v in jsonSchema.items()]
                len1 = len(keyList1)
                keyList += keyList1
        elif 'raw' in reqData['body']:
            raw = reqData['body']['raw']
            jdata = json.loads(raw)
            # 获取所有的请求参数
            keyList1 = [k for k, v in jdata.items()]
            len1 = len(keyList1)
            keyList += keyList1

    if reqData['rest']:
        # 获取所有的请求参数
        keyList2 = [data['name'] for data in reqData['rest'] if data['valid'] and data['enable']]
        len2 = len(keyList2)
        keyList += keyList2
    if reqData['arguments']:
        # 获取所有的请求参数
        keyList3 = [data['name'] for data in reqData['arguments'] if data['valid'] and data['enable']]
        len3 = len(keyList3)
        keyList += keyList3

    # 获取参数枚举组合,接口名称
    # print(reqData['name'])
    list_all_args, sum = getEnum(keyList, reqData['name'], project_name)

    count = 0
    #参数枚举组合添加到ms请求体重
    for args in list_all_args:
        if reqData['body']['kV'] and reqData['body']['valid']:
            for n in range(0, len1):
                if len(keyList) == 1:
                    reqData['body']['kvs'][n]['value'] = args
                else:
                    reqData['body']['kvs'][n]['value'] = args[n]
        elif reqData['body']['json']:
            if 'format' in reqData['body'] and reqData['body']['format'] == 'JSON-SCHEMA':
                if 'properties' in reqData['body']['jsonSchema']:
                    jsonSchema = reqData['body']['jsonSchema']['properties']
                    n = 0
                    for k, v in jsonSchema.items():
                        if len(keyList) == 1:
                            reqData['body']['jsonSchema']['properties'][k]['mock']['mock'] = args
                        else:
                            reqData['body']['jsonSchema']['properties'][k]['mock']['mock'] = args[n]
                        n += 1

            elif 'raw' in reqData['body']:
                temp_args = {}
                for n in range(0, len1):
                    if len(keyList) == 1:
                        temp_args.update({keyList[n]: args})
                    else:
                        temp_args.update({keyList[n]: args[n]})
                #print(temp_args)
                reqData['body']['raw'] = json.dumps(temp_args, ensure_ascii=False)


        # if len(reqData['rest']) > 1:
        for rest in reqData['arguments']:
            if rest['valid'] and rest['enable']:
                m = 0
                for n in range(len1, len1+len2):
                    if len(keyList) == 1:
                        reqData['rest'][m]['value'] = args
                    else:
                        reqData['rest'][m]['value'] = args[n]
                    m += 1

        # if len(reqData['arguments']) > 1:
        for arguments in reqData['arguments']:
            if arguments['valid'] and arguments['enable']:
                m = 0
                for n in range(len1+len2, len1+len2+len3):
                    if len(keyList) == 1:
                        reqData['arguments'][m]['value'] = args
                    else:
                        reqData['arguments'][m]['value'] = args[n]
                    m += 1

        # ===插入断言===
        reqData['hashTree'] = []  # 清空断言数据
        if count < sum:
            reqData['hashTree'].append(assertions_data(True))
        else:
            reqData['hashTree'].append(assertions_data(False))
        count += 1

        # ===header插入token====
        # psot类型的接口且不是login
        if reqData['method'] == 'POST':
                #and 'login' not in reqData['path']:
            token_data = {
                "enable":True,
                "file":False,
                "name":"Authorization",
                "required":True,
                "urlEncode":False,
                "valid":True,
                "value":"${token}"
            }
            if count == 1:
                if len(reqData['headers']) == 1 and not reqData['headers'][0]['valid'] and 'name' not in reqData['headers'][0]:
                    reqData['headers'][0] = token_data
                elif len(reqData['headers']) > 1:
                    if 'name' not in reqData['headers'][len(reqData['headers'])-1] or reqData['headers'][len(reqData['headers'])-1]['name'] == '':  # 有默认，替换
                        reqData['headers'][len(reqData['headers'])-1] = token_data
                    else:  # 没有默认，新增
                        reqData['headers'].append(token_data)
                else:
                    reqData['headers'][0] = token_data



        # 组装成MS的请求体参数
        list_manay.append(json.dumps(reqData, ensure_ascii=False))
    # print(list_manay[0])
    return list_manay

# 断言结果加入
def assertions_data(flag):

    ass_T = {
                    "description":"$.code expect: 000000",
                    "expect":"000000",
                    "expression":"$.code",
                    "option":"REGEX",
                    "type":"JSON",
                    "valid":True
             }
    ass_F = {
                    "description":"$.code not expect: 000000",
                    "expect":"000000",
                    "expression":"$.code",
                    "option":"NOT_EQUALS",
                    "type":"JSON",
                    "valid":True
                }
    ass = {
            "clazzName":"io.metersphere.api.dto.definition.request.assertions.MsAssertions",
            "document":{
                "data":{
                    "json":[

                    ],
                    "jsonFollowAPI":"false",
                    "xml":[

                    ],
                    "xmlFollowAPI":"false"
                },
                "type":"JSON"
            },
            "duration":{
                "type":"Duration",
                "valid":False,
                "value":0
            },
            "jsonPath":[
                # {
                #     "description":"$.code expect: 000000",
                #     "expect":"000000",
                #     "expression":"$.code",
                #     "option":"REGEX",
                #     "type":"JSON",
                #     "valid":True
                # },
                # {
                #     "description":"$.message expect: 成功",
                #     "expect":"成功",
                #     "expression":"$.message",
                #     "option":"REGEX",
                #     "type":"JSON",
                #     "valid":True
                # }
            ],
            "jsr223":[

            ],
            "regex":[

            ],
            "type":"Assertions",
            "xpath2":[

            ],
            "id":"11bd3742-07a4-8cf8-244f-4a499af5b10a",   # id 和 resourceId 暂未发现关联其他，故暂时写死
            "name":"000000断言",
            "resourceId":"669e69b6-d8bd-464b-af2d-e82c948fdfcf",
            "active":True,
            "enable":True,
            "mockEnvironment":False
        }

    if flag:
        ass['jsonPath'].append(ass_T)
    else:
        ass['jsonPath'].append(ass_F)
    return ass



def creat_case(project_id,api_name):
    #根据项目id查询所有的接口定义
    resp = query_by_sql(project_id, api_name)
    pdata = query_args(project_id)
    project_name = pdata[0]['project_name']
    print('project_name is : ' + project_name)
    count = 0
    for i in range(0, len(resp)):
        # print(resp[i]['request'])
        #print("========================接口定义中请求json体======================")

        api_id = resp[i]['id']
        # project_id = resp[i]['project_id']
        name = resp[i]['name']
        # print(project_id)
        num = random.randint(0, 999)
        index = '6' + str(num)
        while (len(index) < 3):
            index += '0'
        # print(index)
        req = analBody(resp[i]['request'], project_name)
        #print(len(req))
        count += len(req)
        ins_manay(project_id, name, api_id, index, req)

    return count

if __name__ == '__main__':
    pid = "3d142ad6-c0d5-492c-9fb2-360970a99bb5"
    # pid = "652794a3-e368-44a8-ba09-cf03831c22aa"
    #
    # projectID = "f60d98f4-e9aa-4176-a4fd-1e6bafd759ea"
    # creat_case(pid, "登录", '绿色金融')
    creat_case(pid, "分页查询用户信息")
    ll = ['bbbbb', 'current', 'hhhh', 'size']
    get_enum_data(ll, '分页查询用户信息', 'demo项目')
    #projectID = "f60d98f4-e9aa-4176-a4fd-1e6bafd759ea"
    #projectID = "52f0e24d-9c78-4b8e-84a7-238695404372"
    #projectID = "652794a3-e368-44a8-ba09-cf03831c22aa"
    # resdata = query_args(projectID)
    # for m in range(len(resdata)):
    #     # print(resdata[m]['request'])
    #     # get_request_args(json.loads(resdata[m]['request']))
    #     analBody(resdata[m]['request'])
    # get_all_args(projectID)
    # pdata = query_args(pid)
    # print(pdata[0]['project_name'])
    # d1 = {'aa':11, 'bb':22}
    # d2 = {'cc':33, 'dd':44}
    # d3 = {'cc':77, 'bb':66}
    # dd = {}
    # dd.update(d1)
    # dd.update(d2)
    # dd.update(d3)
    # print(dd)
    # print(dict(d1.items() + d2.items()))
