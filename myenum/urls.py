from django.conf.urls import url
from django.urls import path

from . import views, views_cron

app_name = 'myenum'
urlpatterns = [
    #path('', views.index, name='index'),
    #path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('save_args/', views.save_args, name='save_args'),
    path('create_case/', views.create_case, name='create_case'),
    path('upload/', views.upload, name='upload'),
    path('cron_job/', views_cron.cron_job, name='cron_job'),
    path('test/', views.test, name='test'),
    path('detail_delete_all/', views.detail_delete_all, name='detail_delete_all'),
    path('<args_name>/', views.detail, name='detail'),
    #path('save/', views.save, name='save'),
    #path('create/', views.create, name='create')
]
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()