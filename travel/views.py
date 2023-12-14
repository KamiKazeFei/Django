from datetime import datetime
from decimal import Decimal
import json
from operator import attrgetter
import os
import uuid
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from common import execute_raw_sql, returnHttpsResponse, save
from travel.models import cost_record, day_introduce, schedule, schedule_file, uploaded_file  # uploaded_file
from rest_framework.response import Response


@transaction.atomic
def getTravelSchedule(request):
    query = f'''
    select
        pk_id,
        title,
        description,
        start_date,
        end_date,
        pass_day              
    from
        travel_schedule
    where 
        isdelete = 'N'
    '''
    try:
        return returnHttpsResponse(False, '', execute_raw_sql(query), '')
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '')


def excuteSave(request):  # 存檔
    body = json.loads(request.body.decode('utf-8'))
    saveData = body['schedule']
    returnObj = save(saveData, 'schedule')
    # 儲存各天的行程
    if 'day_introduces' in saveData.keys():
        for data in list(saveData['day_introduces']):
            response = json.loads(
                save(data, 'day_introduce').content.decode('utf-8'))
            if response.get('error'):
                errorDetail = response.get('error_message')
                return returnHttpsResponse(True, str(errorDetail), [], '')
    # 儲存行程的預算
    if 'cost_records' in saveData.keys():
        for data in list(saveData['cost_records']):
            save(data, 'cost_record')
    # 儲存附檔
    if 'file_list' in saveData.keys():
        for data in list(saveData['file_list']):
            save(data, 'schedule_file')
    return returnObj


def uploadFile(request):  # 上傳檔案
    for key, files in request.FILES.lists():
        fileList = []
        for file in files:
            saveData = uploaded_file()
            saveData.file = file
            saveData.pk_id = str(uuid.uuid4()).replace('-', '')
            saveData.content_type = file.content_type
            saveData.save()
            fileList.append({
                'pk_id': saveData.pk_id,
                'name': file.name,
                'size': file.size,
            })
    return returnHttpsResponse(False, '', fileList, '成功')


def getFileInfo(request):  # 取得上傳檔案
    file_pk_id = request.GET.get('file_pk_id')

    if file_pk_id:
        file = get_object_or_404(uploaded_file, pk_id=file_pk_id)
        # 設置Content-Disposition頭部，這裡設置為直接在瀏覽器中顯示（如果可能）
        response = HttpResponse(
            file.file.read(), content_type=file.content_type)
        response['Content-Disposition'] = 'inline; filename=' + file.file.name

        return response
    else:
        return HttpResponse('File not found.')
    # file = get_object_or_404(uploaded_file, pk_id=request.GET.get('file_pk_id', ''))
    # print(str(file.file))
    # return HttpResponse(file.file)


@transaction.atomic
def excuteQuery(request):  # 執行查詢
    returnData = []
    if len(request.body.decode('utf-8')) > 0:
        body = json.loads(request.body.decode('utf-8'))
        if len(list(body.keys())) > 0:
            # 查詢行程主檔
            travelSchedule = schedule.objects.get(Q(pk_id=body['pk_id']))
            # 查詢每天行程
            introducesList = [model_to_dict(data) for data in day_introduce.objects.filter(
                schedule_pk_id=travelSchedule.pk_id, isdelete='N')]
            # 查詢預算紀錄
            costRecordList = [model_to_dict(data) for data in cost_record.objects.filter(
                schedule_pk_id=travelSchedule.pk_id, isdelete='N')]
            # 查詢附檔
            fileList = [model_to_dict(data) for data in schedule_file.objects.filter(
                schedule_pk_id=travelSchedule.pk_id, isdelete='N')]

            scheduleDict = model_to_dict(travelSchedule)
            scheduleDict['day_introduces'] = sorted(json.loads(json.dumps(
                introducesList, cls=CustomEncoder)), key=(lambda data: data['date']))
            scheduleDict['cost_records'] = sorted(json.loads(json.dumps(
                costRecordList, cls=CustomEncoder)), key=(lambda data: data['ser_no']))
            scheduleDict['file_list'] = sorted(json.loads(json.dumps(
                fileList, cls=CustomEncoder)), key=(lambda data: data['file_name']))

            returnData = [scheduleDict]
        else:
            returnData = list(schedule.objects.all().values())
        return returnHttpsResponse(False, '', returnData, '成功')
    else:
        returnData = schedule.objects.all()
        return returnHttpsResponse(False, '', returnData, '成功')


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, datetime):
            return o.isoformat()
        else:
            return super(CustomEncoder, self).default(o)
