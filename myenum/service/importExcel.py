import pandas as pd
# from django.utils.http import urlquote
# from sqlalchemy import create_engine
from myenum.dao.enum_operation import into_data, query_all


def getExcel():

    file = '/myenum_enum_data.xlsx'
    df = pd.DataFrame(pd.read_excel(file))
    # #df = pd.read_excel(file)
    # constr = "mysql+pymysql://root:%s@10.1.1.86:3307/myenum" % urlquote('Password123@mysql')
    # engine = create_engine(constr, encoding='utf8', pool_pre_ping=True,echo=True, max_overflow=5)
    # df.to_sql('root', con=engine)
    list_data = []
    for i in range(len(df)):
        list_data.append([])

    for k, v in df.to_dict().items():
        c = 0
        for i in range(0, len(v)):
            if str(v[i]) == 'nan':
                v[i] = ''
            list_data[c].append(v[i])
            c += 1
    # print("读取Excel数据为："+str(list_data))

    into_data(list_data)
    # return list_data

if __name__ == '__main__':
    #getExcel()
    ll = [['aa', 'bb'], ['cc','aa']]
    args_list2 = [
        {'id': 2091, 'args_name': 'studyDes', 'project_name': '晋商',
         'a_list': [{'api_name': '保存学习信息', 'api_url': '/emissionCalculate/submitAndExamination', 'mark': '参数描述：学习描述'},
                    {'api_name': '保存学习信息2', 'api_url': '/study/save2', 'mark': '参数描述：学习描述2'}]
         }
    ]
    # yuanlist = [
    #     {'id': 1, 'args_name': 'aaaaaa', 'api_name': '企业分支机构', 'api_url': '/figure/fk/branchInfo', 'project_name': 'demo项目', 'mark': '参数描述：2'},
    #     {'id': 2, 'args_name': 'eid', 'api_name': '企业分支机构', 'api_url': '/figure/fk/branchInfo', 'project_name': 'demo项目', 'mark': '参数描述：3'},
    #     {'id': 3, 'args_name': 'type', 'api_name': '企业分支机构', 'api_url': '/figure/fk/branchInfo', 'project_name': 'demo项目', 'mark': '参数描述：0.待评价，1. 待审核， 2审核驳回， 3. 已完成'},
    #     {'id': 4, 'args_name': 'num', 'api_name': '企业分支机构', 'api_url': '/figure/fk/branchInfo', 'project_name': 'demo项目', 'mark': '参数描述：4'},
    #     {'id': 2279, 'args_name': 'aaaaaa', 'api_name': '兴业企业查询', 'api_url': '/figure/fk/branchInfo','project_name': 'demo项目', 'mark': None},
    #     {'id': 2278, 'args_name': 'num', 'api_name': '兴业企业查询', 'api_url': '/figure/fk/branchInfo','project_name': 'demo项目', 'mark': '555'},
    #     {'id': 33, 'args_name': 'aaaaaa', 'api_name': '广发登录', 'api_url': '/user/login', 'project_name': 'demo项目', 'mark': '参数描述：44455'}
    # ]
    yuanlist = query_all('demo项目')
    temp_dic = {}
    new_list = []
    for mm in range(len(yuanlist)):
        ziji = {x: y for x, y in yuanlist[mm].items() if x in ['project_name', 'api_name', 'api_url', 'mark']}
        ziji2 = {x: y for x, y in yuanlist[mm].items() if x in ['id', 'args_name']}
        new_list.append(ziji2)
        # print(ziji)
        if yuanlist[mm]['args_name'] in temp_dic:
            if ziji not in temp_dic[yuanlist[mm]['args_name']]:
                temp_dic[yuanlist[mm]['args_name']].append(ziji)
        else:
            temp_dic[yuanlist[mm]['args_name']] = [ziji]
    print(temp_dic)
    print(new_list)
    # dd.pop('aaaaaa')
    # print(dd)
    # new_list = []

    for data in new_list:
        for key in list(temp_dic):
            if data['args_name'] == key:
                data.update({'a_list': temp_dic[key]})
                temp_dic.pop(key)

    print(new_list)
    for va in new_list[0:]:
        if 'a_list' not in va:
            new_list.remove(va)

    for i in range(len(new_list)):
        for j in range(len(new_list[i]['a_list'])):
            for k, v in new_list[i]['a_list'][j].items():
                if v is None:
                    new_list[i]['a_list'][j][k] = ''
    print(new_list)
