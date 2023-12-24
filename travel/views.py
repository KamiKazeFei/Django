from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from common import execute_raw_sql, jwt_token_required, returnHttpsResponse, save
from travel.models import cost_record, day_introduce, schedule, schedule_file, uploaded_file, User  # uploaded_file
from PIL import Image
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from email_validator import validate_email, EmailNotValidError


@transaction.atomic
# @jwt_token_required
def getTravelSchedule(request):  # 查詢單檔行程計畫，僅列出必要資訊
    print(request.COOKIES.get('access_token'))
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


# @jwt_token_required
def excuteSave(request):  # 存檔
    # 登入人
    user = request.user
    body = json.loads(request.body.decode('utf-8'))
    saveData = body['schedule']
    returnObj = save(saveData, 'schedule')
    # 儲存各天的行程
    if 'day_introduces' in saveData.keys():
        for data in list(saveData['day_introduces']):
            # data['user_pk_id'] = user.pk_id
            response = json.loads(
                save(data, 'day_introduce').content.decode('utf-8'))
            # 存檔有錯時，直接回傳錯誤
            if response.get('error'):
                errorDetail = response.get('error_message')
                return returnHttpsResponse(True, str(errorDetail), [], '')
    # 儲存行程的預算
    if 'cost_records' in saveData.keys():
        for data in list(saveData['cost_records']):
            # data['user_pk_id'] = user.pk_id
            save(data, 'cost_record')
    # 儲存附檔
    if 'file_list' in saveData.keys():
        for data in list(saveData['file_list']):
            # data['user_pk_id'] = user.pk_id
            save(data, 'schedule_file')
    return returnObj


# @jwt_token_required
def uploadFile(request):  # 上傳檔案
    for key, files in request.FILES.lists():
        fileList = []
        for file in files:
            saveData = uploaded_file()
            saveData.file = file
            saveData.pk_id = str(uuid.uuid4()).replace('-', '')
            saveData.content_type = file.content_type

            obj = {}
            obj['pk_id'] = saveData.pk_id
            obj['name'] = file.name
            obj['size'] = file.size

            if 'image' in file.content_type:
                # 使用 Pillow 打開圖片
                with Image.open(file) as img:
                    width, height = img.size
                    saveData.width = width
                    saveData.height = height
                    obj['width'] = width
                    obj['height'] = height
            elif 'pdf' in file.content_type:
                obj['is_pdf'] = True
            saveData.save()
            fileList.append(obj)
    return returnHttpsResponse(False, '', fileList, '成功')


# @jwt_token_required
def getFileInfo(request):  # 取得上傳檔案    
    file_pk_id = request.GET.get('file_pk_id')
    if file_pk_id:
        file = get_object_or_404(uploaded_file, pk_id=file_pk_id)
        # 設置Content-Disposition頭部，這裡設置為直接在瀏覽器中顯示（如果可能）
        try:
            response = HttpResponse(
                file.file.read(), content_type=file.content_type)
            response['Content-Disposition'] = 'inline; filename=' + \
                file.file.name
            return response
        except FileNotFoundError as e:
            return HttpResponse('查無檔案')
    else:
        return HttpResponse('缺少查詢參數')


@transaction.atomic
def register(request):  # 註冊
    body = json.loads(request.body.decode('utf-8'))
    body['pk_id'] = str(uuid.uuid4()).replace('-', '')
    # 查詢是否有重複使用的帳號 & email
    try:
        user = User.objects.get(
            Q(account=body['account']) | Q(email=body['email']))
        return returnHttpsResponse(True, '已存在重複註冊帳號或Email，請重新再試', [], '')
    # 不存在重複資訊使用者，建立新使用者
    except User.DoesNotExist as e1:
        # 檢查郵件是否符合格式
        try:
            validate_email(body['email'])
        # 不符合就回傳錯誤
        except EmailNotValidError as e:
            return returnHttpsResponse(True, 'EMail格式錯誤，請重新輸入', [], '')
        # 符合就儲存並回傳正常資訊
        else:
            save(body, 'User')
            return returnHttpsResponse(False, '', [], '')
    # 其他錯誤
    except Exception as e3:
        return returnHttpsResponse(True, str(e3), [], '')


@transaction.atomic
def loginCheck(request):  # 登入
    data = json.loads(request.body.decode('utf-8'))
    try:
        # 取得登入者資訊
        loginUser = User.objects.get(Q(Q(email=data['login_id']) | Q(
            account=data['login_id']) & Q(password=data['password'])))
        # 取得驗證Token
        token = getTokensForUser(loginUser)
        # 建立回傳資訊
        response = returnHttpsResponse(False, '登入成功', [], '')

        accessTokenTime = datetime.now().date() + timedelta(days=7)
        refreshTokenTime = datetime.now().date() + timedelta(days=30)

        # 設置Access Token
        response.set_cookie(
            'access_token', token['access'], max_age=86400, expires=accessTokenTime)
        # 設置Refresh Token
        response.set_cookie(
            'refresh_token', token['refresh'], max_age=604800, expires=refreshTokenTime)
        # 回傳資訊
        return response
    except Exception as e:
        return returnHttpsResponse(True, '登入失敗，請確認登入資訊是否正確', [], '')


def getTokensForUser(user):  # 建立JWT Token
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# @jwt_token_required
def logout(request):  # 登出
    response = returnHttpsResponse(False, '已登出', [], '')
    response.set_cookie('ACCESS_TOKEN', '', max_age=0,
                        samesite='none', secure=True)
    response.set_cookie('REFRESH_TOKEN', '', max_age=0,
                        samesite='none', secure=True)
    return response


@transaction.atomic
# @jwt_token_required
def excuteQuery(request):  # 執行查詢
    print(request.COOKIES.get('access_token'))
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
            fileList = []
            for data in schedule_file.objects.filter(schedule_pk_id=travelSchedule.pk_id, isdelete='N'):
                uploadFile = uploaded_file.objects.get(pk_id=data.file_pk_id)
                if data.file_type == 'A':
                    newData = model_to_dict(data)
                    newData['width'] = uploadFile.width
                    newData['height'] = uploadFile.height
                    fileList.append(newData)
                elif 'pdf' in uploadFile.content_type:
                    newData = model_to_dict(data)
                    newData['is_pdf'] = True
                    fileList.append(newData)
                else:
                    fileList.append(model_to_dict(data))

            scheduleDict = model_to_dict(travelSchedule)
            scheduleDict['day_introduces'] = sorted(json.loads(json.dumps(
                introducesList, cls=CustomEncoder)), key=(lambda data: data['date']))
            scheduleDict['cost_records'] = sorted(json.loads(json.dumps(
                costRecordList, cls=CustomEncoder)), key=(lambda data: data['ser_no']))
            scheduleDict['file_list'] = sorted(json.loads(json.dumps(
                fileList, cls=CustomEncoder)), key=(lambda data: data['ser_no']))

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
