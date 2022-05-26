from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class Member(AbstractUser):
    # 身分證
    id_card = models.CharField(max_length=10, unique=True)
    # 生日
    date_of_birth = models.DateField(default=date.today)
    # 手機
    mobile_number = models.CharField(max_length=10)
    # 密碼錯誤次數
    wrong_pwd_times = models.IntegerField(default=0)
    # 是否因密碼錯誤被鎖住
    is_lock = models.BooleanField(default=False)
    # 是否有開戶
    has_open_account = models.BooleanField(default=False)

    # 是否被Ban
    is_ban = models.BooleanField(default=False)
    # 該帳號已不能使用
    cannot_use = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Errortimes(models.Model):
    '''
    紀錄錯誤次數
    '''
    name = models.CharField(max_length=100, primary_key=True)
    value = models.IntegerField()

class MemberData(models.Model):
    '''
    會員開戶資料
    '''

    # 開戶資料 和 Member關聯
    account_data = models.TextField()
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
