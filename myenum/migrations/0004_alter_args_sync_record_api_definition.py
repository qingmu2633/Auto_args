# Generated by Django 3.2.12 on 2022-03-18 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myenum', '0003_args_sync_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='args_sync_record',
            name='api_definition',
            field=models.TextField(blank=True, null=True),
        ),
    ]