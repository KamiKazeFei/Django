import datetime
import decimal
import json
from django.forms.models import model_to_dict
from django.http import JsonResponse
from mysite.settings import SECRET_KEY
from tsp.models import User
import requests
import jwt
from rest_framework import serializers
from django.db import connection
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView, TokenObtainPairView)

from travel.models import cost_record, day_introduce, schedule


jsonheaders = {'Content-Type': 'application/json'}


class HttpsResponse:  # 回傳格式
    def __init__(self, error: bool, error_message: str, data: list, message: str):
        self.error = error
        self.error_message = error_message
        self.data = data
        self.message = message
        self.respone_time = datetime.datetime.now()

    def to_dict(self):
        if self.error == True:
            return {
                "error": self.error,
                "error_message": self.error_message,
                "respone_time": self.respone_time,
            }
        else:
            return {
                "error": self.error,
                "data": self.data,
                "message": self.message,
                "respone_time": self.respone_time
            }


def returnHttpsResponse(error: bool, error_message: str, data: list, message: str):  # 回傳http訊息
    response = JsonResponse(HttpsResponse(
        error, error_message, data, message).to_dict())
    return response


def execute_raw_sql(query: str):  # 執行一般SQL
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result


def save(body: dict, class_name: str):  # 執行存檔
    serializer = ModelSerializer(class_name, data=body)
    existsData = (globals()[class_name]).objects.filter(
        pk_id=body['pk_id']).first()
    try:
        if existsData == None:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            for key, value in body.items():
                setattr(existsData, key, value)
            existsData.save()
        return returnHttpsResponse(False, '', [], '存檔成功')
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '')

    # #
    # # data.save()

    # # 執行存檔
    # try:
    #     # 檢查欄位合法性，除了PK_ID
    #     data.full_clean(exclude=excludeList)
    #     # 轉為字典
    #     saveData = model_to_dict(data)
    #     targetObj = (globals()[class_name]).objects.filter(pk_id=data.pk_id)
    #     targetObjCreateDt = (globals()[class_name]).objects.filter(pk_id=data.pk_id).values('create_dt')
    #     # 如果已存在，則更新資料，否則新增
    #     if len(targetObjCreateDt) > 0:
    #         saveData['version'] += 1
    #         saveData['create_dt'] = targetObjCreateDt[0]['create_dt']
    #         targetObj.update(**saveData)
    #     else:
    #         data.save()
    #     # 回傳資訊
    #     return returnHttpsResponse(False, '', [], '存檔成功')
    # # 偵測到不合法存檔條件
    # except ValidationError as e:
    #     errorKey = [key for key in dict(e).keys()]
    #     errorMessage = '\n'.join(
    #         key + ' : ' + str(dict(e)[key]) for key in errorKey)
    #     return returnHttpsResponse(True, str(errorMessage), [], '')
    # # 其他存檔錯誤
    # except Exception as e:
    #     return returnHttpsResponse(True, str(e), [], '')


def query(request: dict, class_name: str):  # 純資料表查詢ㄐ
    body_unicode = request.body.decode('utf-8')
    body = {key: value for key, value in json.loads(
        body_unicode).items() if value is not None and value != ''}
    member_dicts = [model_to_dict(member) for member in globals()[
        class_name].objects.filter(**body)]
    try:
        return returnHttpsResponse(False, None, member_dicts, '')
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '')


def post(url: str, data: dict):  # 發起POST請求
    response = requests.post(url, data=data)
    if response.status_code == 200:
        result = response.json()
        return JsonResponse({'message': 'POST 請求成功', 'result': result})
    else:
        return JsonResponse({'message': 'POST 請求失敗'}, status=500)


def jwt_token_required(view_func):  # 檢查JWT是否有效
    def wrapped_view(request, *args, **kwargs):
        try:
            if (request.COOKIES is None) or (request.COOKIES.get('ACCESS_TOKEN') is None and request.COOKIES.get('REFRESH_TOKEN') is None):
                return returnHttpsResponse(True, '登入狀態已失效，請重新登入', [], '')
            if request.COOKIES.get('ACCESS_TOKEN') is None and request.COOKIES.get('REFRESH_TOKEN') is not None:
                refreshAccessToken(request)
                wrapped_view(request)
            payload = jwt.decode(
                request.COOKIES['ACCESS_TOKEN'], SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id', None)
            request.user = User.objects.get(pk_id=user_id)
            return view_func(request)
        except jwt.ExpiredSignatureError as e:
            refreshAccessToken(request)
            return wrapped_view(request)
        except jwt.DecodeError as e1:
            return returnHttpsResponse(True, 'JWT解析錯誤，登入失敗', [], '')
    return wrapped_view


def get_client_ip(request):  # 取得登入者IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def refreshAccessToken(request):  # 重新取得驗證Tokenㄠ
    refreshTokenResponse = requests.post(
        'http://127.0.0.1:8000/api/token/refresh/', data={'refresh': request.COOKIES.get('REFRESH_TOKEN')})
    access_token = refreshTokenResponse.json().get('access')
    refresh_token = refreshTokenResponse.json().get('refresh')
    request.COOKIES['ACCESS_TOKEN'] = access_token
    request.COOKIES['REFRESH_TOKEN'] = refresh_token


class ModelSerializer(serializers.ModelSerializer):
    def __init__(self, class_name, *args, **kwargs):
        self.class_name = class_name
        super(ModelSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = None
        fields = '__all__'

    def build_model(self):
        self.Meta.model = globals().get(self.class_name)

    def is_valid(self, *args, **kwargs):
        self.build_model()
        return super(ModelSerializer, self).is_valid(*args, **kwargs)


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        # response = super().post(request, *args, **kwargs)
        try:
            if (request.COOKIES is None) or (request.COOKIES.get('ACCESS_TOKEN') is None and request.COOKIES.get('REFRESH_TOKEN') is None):
                return returnHttpsResponse(True, '登入狀態已失效，請重新登入', [], '')
            if request.COOKIES.get('ACCESS_TOKEN') is None and request.COOKIES.get('REFRESH_TOKEN') is not None:
                refreshAccessToken(request)
            payload = jwt.decode(
                request.COOKIES['ACCESS_TOKEN'], SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id', None)
            request.user = User.objects.get(pk_id=user_id)
            return returnHttpsResponse(False, '', [], '')
        except jwt.ExpiredSignatureError as e:
            refreshAccessToken(request)
            return post(request)
        except jwt.DecodeError as e1:
            return returnHttpsResponse(True, 'JWT解析錯誤，登入失敗', [], '')
