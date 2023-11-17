from django.db import models

# 系統使用者
class User(models.Model):
    # 主鍵
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    # 帳號
    account = models.CharField(max_length=64, null=False, unique=True)
    # 電子郵件
    email = models.EmailField(null=False, unique=True)
    # 密碼
    password = models.CharField(max_length=64, null=False)
    # 使用者名稱
    username = models.CharField(max_length=32, blank=False, null=False, unique=True)    
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)    
    # 建立日
    create_dt = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(null=False,default = 0)
    # 是否已啟用
    is_activate = models.CharField(null=False,default = 'N')

# 旅遊規劃主擋
class User_Planning(models.Model):
    # 外鍵
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    # 主鍵
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    # 使用者PK
    user_pk_id = models.CharField(max_length=32, null=False)
    # 計畫名稱
    planning_name = models.CharField(max_length=126, null=False)
    # 計畫敘述
    planning_description = models.CharField(max_length=1024, null=False)
    # 計畫開始日期
    planning_start_dt = models.DateTimeField(null=False)
    # 計畫結束日期
    planning_end_dt = models.DateTimeField(null=False)
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)
    # 建立日
    create_dt = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(null = False,default = 0)

# 地點
class User_Planning_Place(models.Model):
    # 外鍵
    user_planning = models.ForeignKey( User_Planning, on_delete=models.CASCADE, related_name='user_planning')
    # 規劃PK
    user_planning_pk_id = models.CharField(max_length=32, null=False)
    # 主鍵
    pk_id = models.CharField(max_length=32, null=False, primary_key=True)
    # 地點自訂名稱
    place_name = models.CharField(max_length=126, null=False)
    # 地點描述
    place_description = models.CharField(max_length=2048, null=True)
    # 地點實際名稱
    place_location_name = models.CharField(max_length=512, null=False)
    # 緯度
    lat = models.CharField(max_length=126, null=False)
    # 經度
    lng = models.CharField(max_length=126, null=False)
    # 備註
    memo = models.CharField()
    # 是否刪除
    isdelete = models.CharField(max_length=1, default='N')
    # 刪除日
    delete_dt = models.DateTimeField(null=True, blank=True)
    # 建立日
    create_dt = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    # 最後異動日
    last_update_dt = models.DateTimeField(null=True, blank=True, auto_now=True)
    # 版次
    version = models.IntegerField(null = False,default = 0)
