import json

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from pure_pagination import Paginator, PageNotAnInteger

from myenum.service.analysisArgs import creat_case
from myenum.dao.enum_operation import into_data, query_sync_record_byName, query_args_group, query_by_args, query_all
from myenum.dao.ms_operation import delete_by_sql, query_project, query_project_id
from myenum.models import enum_data
from myenum.service.args_sync import compareMD5
from myenum.service.util_data_enum import get_api_name_list


def index(request):
    if request.method == 'GET':
        #args_list = enum_data.objects.annotate(distinct('args_name')).values('args_name','api_name','project_name','mark')
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # args_list = enum_data.objects.raw('select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data GROUP BY args_name')

        args_list2 = query_args_group('', '')

        types = request.GET.get('types', None)
        # 获取搜索的关键字
        keywords = request.GET.get('keywords', None)
        if types and 'args_name' == types and keywords:
            args_list2 = query_args_group(types, keywords)
        if types and 'api_name' == types and keywords:
            args_list2 = query_args_group(types, keywords)
        if types and 'project_name' == types and keywords:
            args_list2 = query_args_group(types, keywords)

        #获取ms项目名称
        project_name = query_project()
        # print(project_name)
        # api_project = enum_data.objects.raw('select distinct api_name,project_name from myenum_enum_data  where api_name !="" and project_name !=""')
        api_project = query_project_id()
        # print(api_project)
        temp = {}
        for k in api_project:
            if k['id'] in temp:
                temp[k['id']].append(k['api_name'])
            else:
                temp[k['id']] = [k['api_name']]

        p = Paginator(args_list2, per_page=15, request=request)
        args_list = p.page(page)

        # print(project_name)
        return render(request, 'index.html', {'args_list': args_list, 'project_name': project_name, 'api_project': json.dumps(temp, ensure_ascii=False)})

def test(request):
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    args_list = query_all('demo项目')
    # print(args_list)
    args_list2 = [
        {'id': 2091, 'args_name': 'studyDes', 'project_name': '晋商', 'a_list':[{'api_name': '保存学习信息', 'api_url': '/emissionCalculate/submitAndExamination', 'mark': '参数描述：学习描述'},
                                                                              {'api_name': '保存学习信息2', 'api_url': '/study/save2', 'mark': '参数描述：学习描述2'}]},
        {'id': 2092, 'args_name': 'studyDes22', 'project_name': '晋商',
         'a_list': [{'api_name': '保存学习信息', 'api_url': '/dataCenter/updateEntFactoryInfo', 'mark': '参数描述：学习描述'},
                    {'api_name': 'sponsorName', 'api_url': '/study/save2', 'mark': '参数描述：学习描述2'}]},
        {'id': 2093, 'args_name': 'studyDes33', 'project_name': '绿色金融',
         'a_list': [{'api_name': '修改企业信息', 'api_url': '/figure/fk/pageCustomer', 'mark': '参数描述：注册号'},
                    {'api_name': '季度考核指标分析', 'api_url': '/dataCenter/updateEntInfo', 'mark': '参数描述：学习描述2'}]},
    ]

    temp_dic = {}
    new_list = []
    for val in args_list:
        dic_sub1 = {x: y for x, y in val.items() if x in ['project_name', 'api_name', 'api_url', 'mark']}   # dict子集
        dic_sub2 = {x: y for x, y in val.items() if x in ['id', 'args_name']}      # dict子集
        new_list.append(dic_sub2)
        # 合并相同参数的
        if val['args_name'] in temp_dic:
            if dic_sub1 not in temp_dic[val['args_name']]:
                temp_dic[val['args_name']].append(dic_sub1)
        else:
            temp_dic[val['args_name']] = [dic_sub1]

    # 两个子集dict合并
    for data in new_list:
        for key in list(temp_dic):
            if data['args_name'] == key:
                data.update({'a_list': temp_dic[key]})
                temp_dic.pop(key)   # args_name已经比较过的就删掉，防止重复

    # 去重没有a_list的
    for va in new_list[0:]:
        if 'a_list' not in va:
            new_list.remove(va)

    for i in range(len(new_list)):
        for j in range(len(new_list[i]['a_list'])):
            for k, v in new_list[i]['a_list'][j].items():
                if v is None:
                    new_list[i]['a_list'][j][k] = ''

    # print(new_list)
    p = Paginator(new_list, per_page=15, request=request)
    args_list = p.page(page)
    return render(request, 'test.html', {'args_list': args_list})



# 枚举参数详情页面
def detail(request, args_name):
    #print(getEnumConfig.gett())
    if request.method == 'GET':
        print("detail GET================")
        args = query_by_args(args_name)
        api_name_list = get_api_name_list(args_name)
        # print(api_name_list)
        return render(request, 'detail.html', {'args': args, 'api_name_list': api_name_list})

    if request.method == 'POST':
        # print("detail post================")
        if 'save_data' in request.POST:


            # 获取页面选择的项目id
            project_name = request.POST.get('choice')
            api_name = request.POST.get('apiname')
            args_name = request.POST.get("args_name2")
            api_name_list = get_api_name_list(args_name)


            add_data = enum_data()
            add_data.args_name = args_name
            add_data.args_value = request.POST.get("args_value2")
            args_status = request.POST.get("choice2")
            if args_status:
                add_data.args_status = args_status
            else:
                add_data.args_status = "正例"  # 默认正例
            add_data.args_conditions = request.POST.get("args_conditions2")
            add_data.args_api = "0"

            # 当指定接口保存时
            if project_name:
                add_data.project_name = project_name
                add_data.args_api = "1"

            if api_name:
                add_data.project_name = project_name
                add_data.api_name = api_name
                urldata = [data['api_url'] for data in api_name_list[project_name] if data['api_name'] == api_name]
                add_data.api_url = urldata[0]
                mark = [data['mark'] for data in api_name_list[project_name] if data['api_name'] == api_name]
                add_data.mark = mark[0]
                add_data.args_api = "1"

            add_data.update_time = timezone.now()
            add_data.save()

            args = query_by_args(request.POST.get("args_name2"))
            api_name_list = get_api_name_list(args_name)
            return render(request, 'detail.html', {'args': args, 'api_name_list': api_name_list})

        if 'delete_data' in request.POST:
            tags = request.POST.getlist("tags")
            if tags == []:
                return HttpResponse("请勾选")

            # 删除选中
            for tag in tags:
                enum_data.objects.filter(pk=tag).delete()

            args_name = request.POST.get("args_name2")
            args = query_by_args(request.POST.get("args_name2"))
            api_name_list = get_api_name_list(args_name)
            return render(request, 'detail.html', {'args': args, 'api_name_list': api_name_list})

# 参数枚举值详情页面批量删除
def detail_delete_all(request):
    # tags = request.POST.getlist("tags")
    # if tags == []:
    #     return HttpResponse("请勾选")
    if request.is_ajax():
        print(request.body)
        # print(request.POST)
        # print(request.POST)

        json_bytes = request.body
        json_dict = json.loads(json_bytes)  # 直接将二进制的json格式字符串进行解码和反序列化
        # json_dict = {'id': ['1','2'], 'args_name': 'a04291' }
        print(json_dict)
        # 删除选中
        for tag in json_dict['id']:
            enum_data.objects.filter(pk=tag).delete()
        # for tag in json_dict:
        #     enum_data.objects.filter(pk=tag).delete()

        # args_name = 'aaa0429'
        args_name = json_dict['args_name']
        print(args_name)
        args = query_by_args(args_name)
        api_name_list = get_api_name_list(args_name)
        return render(request, 'detail.html', {'args': args, 'api_name_list': api_name_list})

#保存参数
def save_args(request):
    if request.method == 'POST':
        # print("create POST================")
        if request.POST.get("argsName0"):
            add_data = enum_data()
            add_data.args_name = request.POST.get("argsName0")
            add_data.save()

            return render(request, 'result.html', {"message": "保存成功"})
        else:
            return render(request, 'result.html', {"message": "请录入参数名称！"})

# 生成用例
def create_case(request):
    if request.method == 'GET':
        # print("create GET================")
        return HttpResponse("保存成功")

    if request.method == 'POST':
        #获取页面选择的项目id
        project_id = request.POST.get('choice')
        api_name = request.POST.get('apiname')

        # print(project_id)
        # print(api_name)
        # 保存用例
        if 'case_save' in request.POST:
            if project_id:
                num = creat_case(project_id, api_name)
                return render(request, 'result.html', {"message": "共生成用例 "+str(num)+" 个"})
            else:
                return render(request, 'result.html', {"message": "请选择项目！"})

        # 删除用例
        if 'case_del' in request.POST:
            if project_id:
                delete_by_sql(project_id, api_name)
                return render(request, 'result.html', {"message": "删除用例成功"})
            else:
                return render(request, 'result.html', {"message": "请选择项目！"})

        # 同步所有接口定义的参数
        if 'sync_args' in request.POST:
            if project_id:
                mess = compareMD5(project_id)
                if type(mess) == type(0):
                    message = "共同步参数：" + str(mess) + "个"
                else:
                    message = mess
                return render(request, 'result.html', {"message": message})
            else:
                return render(request, 'result.html', {"message": "请选择项目！"})


# excel导入参数枚举值
def upload(request):
    if request.method == 'POST':
        myfile = request.FILES.get('myfile', None)
        if not myfile:
            return HttpResponse("文件未上传")

        excel_type = myfile.name.split('.')[1]
        if excel_type in ['xls', 'xlsx']:
            df = pd.DataFrame(pd.read_excel(myfile))
            # print(df)
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

            # print('--------------------')
            # print("读取Excel数据为：" + str(list_data))
            for i in range(0, len(list_data)):
                if list_data[i][4] != '':    #模板字段长度
                    list_data[i].append("1")
                else:
                    list_data[i].append("0")
            # print('--------------------')
            # print("读取Excel数据为：" + str(list_data))
            into_data(list_data)

        return render(request, 'result.html', {"message": "导入参数枚举值成功"})