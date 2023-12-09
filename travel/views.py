from datetime import datetime
from decimal import Decimal
import json
from operator import attrgetter
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from common import execute_raw_sql, returnHttpsResponse, save
from travel.models import cost_record, day_introduce, schedule

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
    return returnObj


@transaction.atomic
def excuteQuery(request):  # 執行查詢
    returnData = []
    if len(request.body.decode('utf-8')) > 0:
        body = json.loads(request.body.decode('utf-8'))
        if len(list(body.keys())) > 0:
            travelSchedule = schedule.objects.get(Q(pk_id=body['pk_id']))
            introducesList = [model_to_dict(data) for data in day_introduce.objects.filter(
                schedule_pk_id=travelSchedule.pk_id, isdelete='N')]

            costRecordList = [model_to_dict(data) for data in cost_record.objects.filter(
                schedule_pk_id=travelSchedule.pk_id, isdelete='N')]

            scheduleDict = model_to_dict(travelSchedule)
            scheduleDict['day_introduces'] = introducesList
            scheduleDict['cost_records'] = sorted(json.loads(json.dumps(costRecordList, cls=CustomEncoder)), key=(lambda data : data['ser_no'])) 
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
