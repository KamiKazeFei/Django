from django.db import models
from django.utils import timezone
# Create your models here.

# 成員資訊


class Member(models.Model):
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    name = models.CharField(max_length=8, blank=False, null=False)
    address = models.CharField(max_length=256, blank=False, null=False)
    email = models.EmailField(max_length=64, blank=False, null=False)
    phone = models.CharField(max_length=64, blank=False, null=False)
    age = models.IntegerField(blank=False, null=False)
    memo = models.CharField(max_length=512, blank=True, null=True)
    isdelete = models.CharField(max_length=1, default='N')
    delete_dt = models.DateTimeField(null=True, blank=True)
    create_dt = models.DateTimeField(null=True, blank=True)
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)

    # @property
    # def b_list(self):
    #     # 获取b_list的值
    #     return self._b_list

    # @b_list.setter
    # def b_list(self, value):
    #     # 设置b_list的值
    #     self._b_list = value

    # def save_b_list_to_database(self):
    #     # 将_b_list中的数据保存到数据库中
    #     for data in self._b_list:
    #         saveData(data)


class Member_Order(models.Model):
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    memeber_pk_id = models.ForeignKey(Member, to_field='pk_id', on_delete=models.CASCADE)
    order_name = models.CharField(max_length=126, null=False)
    order_detail = models.CharField(max_length=512, null=False)
    order_amout = models.IntegerField(default=0, null=False)
    order_price = models.IntegerField(default=0, null=False)
    order_total_price = models.IntegerField(default=0, null=False)
    memo = models.CharField(max_length=512, blank=True, null=True)
    isdelete = models.CharField(max_length=1, default='N')
    delete_dt = models.DateTimeField(null=True, blank=True)
    create_dt = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
