import datetime
import json
from django.forms.models import model_to_dict
from django.http import JsonResponse
from mysite.settings import SECRET_KEY
from travel.models import uploaded_file, cost_record, day_introduce, schedule, schedule_file, User
import requests
import jwt
from rest_framework import serializers
from django.db import connection
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView, TokenObtainPairView)
from django.utils import timezone
from datetime import timedelta

jsonheaders = {'Content-Type': 'application/json'}


class HttpsResponse:  # 回傳格式
    def __init__(self, error: bool, error_message: str, data: list, message: str):
        self.error = error
        self.error_message = error_message
        self.data = data
        self.message = message
        self.respone_time = timezone.now()

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


def returnHttpsResponse(error: bool, error_message: str, data: list, message: str, request=None):  # 回傳http訊息
    response = JsonResponse(HttpsResponse(
        error, error_message, data, message).to_dict())
    # 如果需要更換token
    if (request is not None):
        if ('required_reset_access' in request.session) and (request.COOKIES.get('new_access_token') is not None):
            accessTokenTime = timezone.now().date() + timedelta(days=1)
            response.set_cookie('access_token', request.COOKIES.get('access_token'), max_age=86400, expires=accessTokenTime)
    return response


def execute_raw_sql(query: str, condition_variable: list):  # 執行一般SQL
    with connection.cursor() as cursor:
        cursor.execute(query, condition_variable)
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result


def save(body: dict, class_name: str, request=None):  # 執行存檔
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

            existsData.last_update_dt = timezone.now()
            existsData.save()
        return returnHttpsResponse(False, '', [], '存檔成功', request)
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '', request)


def query(request: dict, class_name: str):  # 純資料表查詢
    body_unicode = request.body.decode('utf-8')

    body = {key: value for key, value in json.loads(
        body_unicode).items() if value is not None and value != ''}

    member_dicts = [model_to_dict(member) for member in globals()[
        class_name].objects.filter(**body)]
    try:
        return returnHttpsResponse(False, None, member_dicts, '', request)
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '', request)


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
            # 如果cookies是空的，或是沒有包含acces_token跟refresh的話，都視為未登入
            if (request.COOKIES is None) or (request.COOKIES.get('access_token') is None and request.COOKIES.get('refresh_token') is None):
                return returnHttpsResponse(True, '登入狀態已失效，請重新登入', [], '')
            # 如果只有refresh，使用refresh Token更新
            if (request.COOKIES.get('access_token') is None) and (request.COOKIES.get('refresh_token') is not None):
                request = refreshAccessToken(request)

            payload = jwt.decode(request.COOKIES['access_token'], SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id', None)
            request.user = User.objects.get(pk_id=user_id)
            return view_func(request)

        # Token已經過期
        except jwt.ExpiredSignatureError as e:
            request = refreshAccessToken(request)
            payload = jwt.decode(request.COOKIES['access_token'], SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id', None)
            request.user = User.objects.get(pk_id=user_id)
            return wrapped_view(request)

        # 解析錯誤
        except jwt.DecodeError as e1:
            return returnHttpsResponse(True, 'JWT解析錯誤,登入失敗', [], '')
    return wrapped_view


def get_client_ip(request):  # 取得登入者IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def refreshAccessToken(request):  # 重新取得驗證Token
    refreshTokenResponse = requests.post('http://kamikaze.website:8000/api/token/refresh/', data={'refresh': request.COOKIES.get('refresh_token')})
    request.COOKIES['access_token'] = refreshTokenResponse.json().get('access')
    request.COOKIES['new_access_token'] = refreshTokenResponse.json().get('access')
    request.session['required_reset_access'] = True
    return request


class ModelSerializer(serializers.ModelSerializer):                       # 模型序列化
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
            if (request.COOKIES is None) or (request.COOKIES.get('access_token') is None and request.COOKIES.get('refresh_token') is None):
                return returnHttpsResponse(True, '登入狀態已失效，請重新登入', [], '')
            if request.COOKIES.get('access_token') is None and request.COOKIES.get('refresh_token') is not None:
                refreshAccessToken(request)
            payload = jwt.decode(
                request.COOKIES['access_token'], SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id', None)
            request.user = User.objects.get(pk_id=user_id)
            return returnHttpsResponse(False, '', [], '')
        except jwt.ExpiredSignatureError as e:
            refreshAccessToken(request)
            return post(request)
        except jwt.DecodeError as e1:
            return returnHttpsResponse(True, 'JWT解析錯誤，登入失敗', [], '')
