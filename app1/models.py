from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class Member(AbstractUser):
    '''
    會員註冊
    '''    

    id_card = models.CharField(max_length=10, unique=True)
    
    date_of_birth = models.DateField(default=date.today)
    
    mobile_number = models.CharField(max_length=10)
    
    wrong_pwd_times = models.IntegerField(default=0)
    
    is_lock = models.BooleanField(default=False)
    
    has_open_account = models.BooleanField(default=False)
    
    is_ban = models.BooleanField(default=False)    

    def __str__(self):
        return self.username

    @property
    def increase_errortime(self, times = 1):
        self.wrong_pwd_times += times
        self.save()

    @property
    def is_ban_on(self):
        self.is_ban = True
        self.save()

    @property
    def is_active_off(self):
        self.is_active = False
        self.save()

    @property
    def is_lock_on(self):        
        self.is_lock = True
        self.save()


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

    account_data = models.TextField()
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
