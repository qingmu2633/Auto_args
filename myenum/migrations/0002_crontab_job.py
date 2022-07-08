# Generated by Django 3.2.12 on 2022-03-17 02:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myenum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='crontab_job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(blank=True, max_length=200, null=True)),
                ('project_id', models.CharField(blank=True, max_length=50, null=True)),
                ('webhook', models.CharField(blank=True, max_length=200, null=True)),
                ('is_status', models.CharField(blank=True, max_length=10, null=True)),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='update_time')),
            ],
            options={
                'verbose_name': '定时任务配置',
            },
        ),
    ]