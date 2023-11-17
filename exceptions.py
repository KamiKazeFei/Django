from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from common import returnHttpsResponse


def custom_exception_handler(exc, context):
    # response = exception_handler(exc, context)
    if isinstance(exc):
        return returnHttpsResponse(True, '登入憑證已過期，請重新登入')
