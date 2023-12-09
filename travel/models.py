import datetime
from django.db import models


class schedule(models.Model):  # 旅行計畫
    # 使用者pk
    user_pk_id = models.CharField(max_length=32, null=True)
    # 主鍵
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    # 行程標題
    title = models.CharField(max_length=128, null=False)
    # 行程說明
    description = models.CharField(max_length=1024, null=False)
    # 起始日
    start_date = models.DateTimeField(null=True, blank=True)
    # 結束日
    end_date = models.DateTimeField(null=True, blank=True)
    # 旅行天數
    pass_day = models.IntegerField(null=False)
    # 預計花費
    preparation_cost = models.IntegerField(null=True)
    # 實際花費
    real_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, null=True)
    # 旅程備註
    memo = models.CharField(max_length=512, null=True)
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)
    # 建立日
    create_dt = models.DateTimeField(
        null=True, blank=True, default=datetime.datetime.now)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(null=False, default=0)


class day_introduce(models.Model):
    # 子檔 TravelDayIntroduce 的模型
    # schedule = models.ForeignKey(
    #     schedule, on_delete=models.CASCADE, related_name='day_introduces')
    # 序號
    ser_no = models.IntegerField(null=True)
    # 主鍵
    pk_id = models.CharField(max_length=32, primary_key=True)
    # 行程PK
    schedule_pk_id = models.CharField(max_length=32, null=False)
    # 行程介紹
    schedule_list = models.JSONField(null=True)
    # 日期
    date = models.DateTimeField(null=True)
    # 當日標題
    title = models.CharField(max_length=64, null=True)
    # 當日說明
    description = models.CharField(max_length=128, null=True)
    # 旅店名稱
    hotel_name = models.CharField(max_length=128, null=True)
    # 旅店位置網址
    hotel_map_location = models.CharField(max_length=2048, null=True)
    # 購物清單
    shopping_detail = models.JSONField(null=True)
    # 備註清單
    memo = models.JSONField(null=True)
    # 早餐
    breakfirst = models.CharField(max_length=128, null=True)
    # 早餐位置
    breakfirst_map_location = models.CharField(max_length=2048, null=True)
    # 午餐
    launch = models.CharField(max_length=128, null=True)
    # 午餐位置
    launch_map_location = models.CharField(max_length=2048, null=True)
    # 晚餐
    dinner = models.CharField(max_length=128, null=True)
    # 晚餐位置
    dinner_map_location = models.CharField(max_length=2048, null=True)
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)
    # 建立日
    create_dt = models.DateTimeField(
        null=True, blank=True, default=datetime.datetime.now)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(default=0, null=True)


class cost_record(models.Model):
    # 子檔 TravelDayIntroduce 的模型
    # schedule = models.ForeignKey(
    #     schedule, on_delete=models.CASCADE, related_name='cost_records')
    # 主鍵
    pk_id = models.CharField(max_length=32, primary_key=True)
    # 行程PK
    schedule_pk_id = models.CharField(max_length=32, null=False)
    # 序號
    ser_no = models.IntegerField(max_length=6, null=False)
    # 花費類型
    type = models.CharField(max_length=8, null=True)
    # 說明
    description = models.CharField(max_length=512, null=True)
    # 花費金額
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    # 幣別
    currency_type = models.CharField(max_length=16, default='TWD', null=True)
    # 匯率
    exchange_rate = models.DecimalField(
        max_digits=15, decimal_places=8, default=1, null=True)
    # 計算後成本
    final_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, null=True)
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)
    # 建立日
    create_dt = models.DateTimeField(
        null=True, blank=True, default=datetime.datetime.now)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(default=0, null=True)


class TravelDaySchedule:
    # 行程PK
    introduce_pk_id: str
    # 行程時間
    time: str
    # 行程介紹圖片
    pic_src: str
    # 行程說明
    description: str
    # 行程位置網址
    map_location: str
