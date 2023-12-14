# Generated by Django 4.2.4 on 2023-12-09 09:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0021_rename_file_name_uploaded_file_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploaded_file',
            name='create_dt',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AddField(
            model_name='uploaded_file',
            name='delete_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='uploaded_file',
            name='isdelete',
            field=models.CharField(default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='uploaded_file',
            name='last_update_dt',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='uploaded_file',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cost_record',
            name='ser_no',
            field=models.IntegerField(),
        ),
    ]
