from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone

from django.shortcuts import render
from myenum.dao.ms_operation import query_project
from myenum.models import crontab_job

# 跳转定时任务配置
def cron_job(request):
    if request.method == 'GET':
        # print('=======get==============')
        # 获取ms项目名称
        project_name = query_project()
        cron_job = crontab_job.objects.all()
        return render(request, 'crontab.html', {"project_name": project_name, "cron_job": cron_job})

    if request.method == 'POST':
        # print('=======POST==============')
        if 'check_status' in request.POST:
            tags = request.POST.getlist("tags")
            if tags == []:
                return HttpResponse("请勾选")

            # 启停用
            for tag in tags:
                cron_obj = crontab_job.objects.filter(pk=tag)
                for cron in cron_obj:
                    if cron.is_status == '1':
                        crontab_job.objects.filter(pk=tag).update(is_status="0")
                    else:
                        crontab_job.objects.filter(pk=tag).update(is_status="1")
            # 获取ms项目名称
            project_name = query_project()
            cron_job = crontab_job.objects.all()
            return render(request, 'crontab.html', {"project_name": project_name, "cron_job": cron_job})

        if 'save_data' in request.POST:
            add_cron = crontab_job()
            add_cron.project_name = request.POST.get("project_name")
            add_cron.project_id = request.POST.get("project_id")
            add_cron.webhook = request.POST.get("webhook")
            add_cron.is_status = request.POST.get("job_status")
            add_cron.update_time = timezone.now()
            add_cron.save()

            # 获取ms项目名称
            project_name = query_project()
            cron_job = crontab_job.objects.all()
            return render(request, 'crontab.html', {"project_name": project_name, "cron_job": cron_job})

        if 'delete_data' in request.POST:
            tags = request.POST.getlist("tags")
            if tags == []:
                return HttpResponse("请勾选")

            for tag in tags:
                crontab_job.objects.filter(pk=tag).delete()

            # 获取ms项目名称
            project_name = query_project()
            cron_job = crontab_job.objects.all()
            return render(request, 'crontab.html', {"project_name": project_name, "cron_job": cron_job})

