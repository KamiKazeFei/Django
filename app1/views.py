from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.http import JsonResponse

from common import returnHttpsResponse
from .models import Member, Member_Order
import json


@csrf_exempt
def query(request):
    body_unicode = request.body.decode('utf-8')
    body = {key: value for key, value in json.loads(
        body_unicode).items() if value is not None and value != ''}
    member_dicts = [model_to_dict(member)
                    for member in Member.objects.filter(**body)]
    return JsonResponse({"error": False, "data": member_dicts})


@csrf_exempt
def excuteSaveMember(request):  # 修改
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    returnObj = None
    if str(type(body)).split("'")[1] == 'dict':
        returnObj = saveMember(body)
        return returnObj
    elif str(type(body)).split("'")[1] == 'list':
        for singleBody in body:
            returnObj = saveMember(singleBody)
        return returnObj


def saveMember(body: dict):
    memberOrderList = body['member_order_list']
    body = {key: value for key, value in body.items() if key in (
        ele.name for ele in Member._meta.local_concrete_fields)}
    for key, value in body.items():
        if value == '':
            body[key] = None
    data = Member(**body)
    response = saveMemberData(data)
    if memberOrderList is not None:
        for detail in memberOrderList:
            saveMemberOrderData(data, detail)
        return response
    else:
        return response


def saveMemberData(data: Member):
    try:
        data.full_clean(exclude=['pk_id'])
        saveData = model_to_dict(data)
        if data.create_dt is not None:
            Member.objects.filter(pk_id=data.pk_id).update(**saveData)
        else:
            data.save()
        return returnHttpsResponse(False, '', [], '存檔成功')
    except ValidationError as e:
        errorKey = [key for key in dict(e).keys()]
        errorMessage = '\n'.join(
            key + ' : ' + str(dict(e)[key]) for key in errorKey)
        return returnHttpsResponse(True, str(errorMessage), [], '')
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '')


def saveMemberOrderData(member: Member, memberOrderDict: dict):
    memberOrderDict = {key: value for key, value in memberOrderDict.items(
    ) if key in (ele.name for ele in Member_Order._meta.local_concrete_fields)}
    for key, value in memberOrderDict.items():
        if value == '':
            memberOrderDict[key] = None
    memberOrder = Member_Order(**memberOrderDict)
    try:
        memberOrder.full_clean(exclude=['pk_id'])
        saveData = model_to_dict(memberOrder)
        if memberOrder.create_dt is not None:
            Member_Order.objects.filter(pk_id=memberOrder.pk_id).update(
                parent=member, **saveData)
        else:
            memberOrder.save(parent=member)
        return returnHttpsResponse(False, '', [], '存檔成功')
    except ValidationError as e:
        errorKey = [key for key in dict(e).keys()]
        errorMessage = '\n'.join(
            key + ' : ' + str(dict(e)[key]) for key in errorKey)
        return returnHttpsResponse(True, str(errorMessage), [], '')
    except Exception as e:
        return returnHttpsResponse(True, str(e), [], '')
