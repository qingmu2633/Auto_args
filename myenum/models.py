from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone


class enum_data(models.Model):
    args_name = models.CharField(max_length=200)
    project_name = models.CharField(max_length=200, blank=True, null=True)
    api_name = models.CharField(max_length=200, blank=True, null=True)   #参数名称
    api_url = models.CharField(max_length=100, blank=True, null=True)  # 参数url
    args_value = models.CharField(max_length=1000, blank=True, null=True)   #参数枚举值
    args_status = models.CharField(max_length=10, blank=True, null=True)    #参数名称正反例状态
    args_conditions = models.CharField(max_length=200, blank=True, null=True)   #参数枚举条件
    args_api = models.CharField(max_length=10, blank=True, null=True)  #是否指定接口
    mark = models.CharField(max_length=1000, blank=True, null=True)
    # maximum = models.CharField(max_length=500, blank=True, null=True)
    # minimum = models.CharField(max_length=500, blank=True, null=True)
    # max_length = models.CharField(max_length=500, blank=True, null=True)
    # min_length = models.CharField(max_length=500, blank=True, null=True)
    update_time = models.DateTimeField('update_time', default=timezone.now)
    #create_time = models.TimeField()

    def __str__(self):
        return self.args_name

    # class Meta:
    #     verbose_name = '参数名字'

class crontab_job(models.Model):
    project_name = models.CharField(max_length=200, blank=True, null=True)
    project_id = models.CharField(max_length=50, blank=True, null=True)
    webhook = models.CharField(max_length=200, blank=True, null=True)
    is_status = models.CharField(max_length=10, blank=True, null=True)
    update_time = models.DateTimeField('update_time', default=timezone.now)

    def __str__(self):
        return self.project_id

    class Meta:
        verbose_name = '定时任务配置'


class args_sync_record(models.Model):
    project_name = models.CharField(max_length=200, blank=True, null=True)
    project_id = models.CharField(max_length=50, blank=True, null=True)
    api_definition = models.TextField(blank=True, null=True)
    api_md5 = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField('update_time', default=timezone.now)

    def __str__(self):
        return self.project_id

    class Meta:
        verbose_name = '接口定义json'