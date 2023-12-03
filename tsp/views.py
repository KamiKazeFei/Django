
from django.forms import model_to_dict
import jwt
from rest_framework import status
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from common import jwt_token_required, returnHttpsResponse, save, query, get_client_ip
from django.db import connection
from django.db.models import Q
from .models import User
import json
from django.contrib.sessions.models import Session

# 查詢使用者資料


@jwt_token_required
def queryTspUser(request):
    return query(request, 'User')


# 執行存檔，針對多檔 & 單檔處理進行判別
def excuteSaveTspUser(request):  # 修改
    returnObj = None
    body = json.loads(request.body.decode('utf-8'))
    if str(type(body)).split("'")[1] == 'dict':
        returnObj = save(body, 'User')
    elif str(type(body)).split("'")[1] == 'list':
        for singleBody in body:
            returnObj = save(singleBody, 'User')
    return returnObj

# 檢查電子郵件、帳號 、使用者名稱有無重複


def infoDuplicateCheck(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        User.objects.get(Q(email__contains=data['email']) | Q(
            account__contains=data['account']) | Q(username__contains=data['username']))
        return returnHttpsResponse(True, '帳號或郵件或使用者名稱存在重複資訊，請嘗試輸入其他資料', [], '')
    except Exception as e:
        return returnHttpsResponse(False, '註冊成功，將導向至登入頁面', [], '')

# 登入檢查


@csrf_exempt
def loginCheck(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        loginUser = User.objects.get(Q(Q(email=data['login_id']) | Q(
            account=data['login_id']) & Q(password=data['password'])))
        token = getTokensForUser(loginUser)
        response = returnHttpsResponse(False, '登入成功', [token], '')
        response.set_cookie(
            'ACCESS_TOKEN', token['access'], max_age=3600, samesite='none', secure=True)
        response.set_cookie(
            'REFRESH_TOKEN', token['refresh'], max_age=25200, samesite='none', secure=True)
        return response
    except Exception as e:
        return returnHttpsResponse(True, '查無此帳號，請確認登入資訊', [], '')


# 回傳JWT Token
def getTokensForUser(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# 檢查JWT是否有效
def checkJWTtoken(request):
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            return JsonResponse({'error': 'JWT token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'JWT token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return JsonResponse({'error': 'JWT token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)


# 登出
def logout(request):
    response = returnHttpsResponse(False, '已登出', [], '')
    response.set_cookie('ACCESS_TOKEN', '', max_age=0,
                        samesite='none', secure=True)
    response.set_cookie('REFRESH_TOKEN', '', max_age=0,
                        samesite='none', secure=True)
    return response
