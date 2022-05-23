from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.


class Member(AbstractUser):
    #身分證
    id_card = models.CharField(max_length=10,unique=True)
    #生日
    date_of_birth = models.DateField(default=date.today)
    #手機
    mobile_number = models.CharField(max_length=10)
    #密碼錯誤次數
    wrong_pwd_times = models.IntegerField(default=0)
    #是否因密碼錯誤被鎖住
    is_lock = models.BooleanField(default=False)
    #是否有開戶
    has_open_account = models.BooleanField(default=False)

    def __str__(self):
        return self.username