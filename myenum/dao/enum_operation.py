from datetime import datetime
from myenum.dao.db_myenum import MysqlPool

ms = MysqlPool()
def getEnumData(queryList):
    inlist = "\""
    for v in queryList:
        inlist = inlist + v + "\",\""
    # print(str(inlist[0: len(inlist)-2]))
    #where args_name in (%s)
    sql = """select args_name,args_value,args_status,api_name,project_name, mark ,args_api from myenum_enum_data where binary args_name in (%s)""" % (str(inlist[0: len(inlist)-2]))
    # sql_api = """select args_name,args_value,args_status,api_name, mark ,args_api from myenum_enum_data where args_api is NULL and binary args_name in (%s)""" % (apiname, str(inlist[0: len(inlist)-2]))
    # print(sql)
    d = ms.fetch_all(sql)
    # d_api = ms.fetch_all(sql_api)
    # print(d)
    return d


#主要是excel导入使用
def into_data(data):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO `myenum`.`myenum_enum_data` (`args_name`, `args_status`, `args_value`,`args_conditions`,`api_name`,`args_api`, `update_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    params = ((data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], data[i][5], dt_string) for i in range(0, len(data)))
    # print(type(dt_string))
    # print(type(data[0][0]))
    ms.insert_many(sql, params)
    print('====插入数据完成====')


def into_sync_data(data):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO `myenum`.`myenum_enum_data` (`args_name`, `api_name`, `api_url`, `project_name`,`mark`, `args_status`,`args_api`, `update_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    params_t = ((data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], '正例', '1', dt_string) for i in range(0, len(data)))
    params_f = ((data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], '反例', '1', dt_string) for i in range(0, len(data)))

    ms.insert_many(sql, params_t)
    ms.insert_many(sql, params_f)
    # print('====项目初始化插入参数数据完成====')


def query_cron_job():
    sql = """select project_id, webhook from `myenum`.`myenum_crontab_job` where is_status = '1'"""
    cron_job = ms.fetch_all(sql)
    return cron_job


def into_sync_record(data):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO `myenum`.`myenum_args_sync_record` (`project_name`, `project_id`, `api_definition`,`api_md5`, `update_time`) VALUES (%s,%s,%s,%s,%s)"""
    ms.insert(sql, (data[0], data[1], data[2], data[3], dt_string))
    # print('====插入接口定义数据完成====')

def into_test_sync_record(data):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    sql = """INSERT INTO `myenum`.`test_sync_record` (`project_name`, `project_id`, `api_definition`,`api_md5`, `update_time`) VALUES (%s,%s,%s,%s,%s)"""
    ms.insert(sql, (data[0], data[1], data[2], data[3], dt_string))
    # print('====插入接口定义数据完成====')

def query_sync_record_byID(project_id):
    sql = """select project_name, api_definition, api_md5 from `myenum`.`myenum_args_sync_record` where project_id = '%s' ORDER BY id desc  limit 1""" % project_id
    # print(sql)
    sync_record = ms.fetch_all(sql)
    return sync_record

def query_test_sync_record_byID(project_id):
    sql = """select api_md5 from `myenum`.`test_sync_record` where project_id = '%s' ORDER BY id desc  limit 1""" % project_id
    # print(sql)
    sync_record = ms.fetch_all(sql)
    return sync_record


def query_sync_record_byName():
    # sql = """select project_name, project_id, api_definition from `myenum`.`myenum_args_sync_record` where project_name = '%s' ORDER BY update_time desc  limit 1""" % project_name
    sql = """select project_name, project_id, api_definition from myenum_args_sync_record where id  in(select MAX(id) from myenum_args_sync_record GROUP BY project_name)"""
    sync_record = ms.fetch_all(sql)
    return sync_record

def query_args_group(types, keywords):

    sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data GROUP BY binary args_name"""
    if types and 'args_name' == types and keywords:
        sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data where args_name = '%s' GROUP BY binary args_name""" % keywords
    if types and 'api_name' == types and keywords:
        sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data where api_name = '%s' GROUP BY binary args_name""" % keywords
    if types and 'project_name' == types and keywords:
        sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data where project_name = '%s' GROUP BY binary args_name""" % keywords

    args_group = ms.fetch_all(sql)
    return args_group

def query_by_args(keywords):

    sql = """select id,args_name,api_name,args_value,mark,project_name,args_conditions,args_status,api_url,args_api from myenum_enum_data where binary args_name = '%s'""" % keywords
    args_group = ms.fetch_all(sql)
    return args_group

def query_all(keywords):
    # sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data where project_name = '%s'""" % keywords
    sql = """select id,args_name,api_name,api_url,project_name,mark from myenum_enum_data """
    args_group = ms.fetch_all(sql)
    return args_group

