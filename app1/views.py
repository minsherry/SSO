import random

from io import StringIO
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from enums.AuthStatusEnum import *
from enums.ErrorStrEnum import *
from .models import Errortimes, Member
from .serializers import *

class AuthUserInfo(GenericAPIView):

    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer
    
    def format_check(self, request):
        
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():            
            result = user_data_auth_result(False, None)        
        else :                   
            result = user_data_auth_result(True, serializer.validated_data)            

        return result
    
    def check_by_specified_column(self, **kwargs):

        try:

            member = Member.objects.get(**kwargs)            

            result = user_data_auth_result(True, member)

            return result

        except Exception:

            result = user_data_auth_result(False, None)

            return result
    
    def third_check_other_column(self, db_data, request_data):
        
        tmp_str = StringIO()

        if request_data.get('id_card') != db_data.id_card:            
            tmp_str.write("身分證/")

        if request_data.get('date_of_birth') != db_data.date_of_birth:            
            tmp_str.write("出生年月日/")

        if request_data.get('mobile_number') != db_data.mobile_number:
            tmp_str.write("連絡電話/")                 

        if tmp_str.getvalue():
            result = user_data_auth_result(False, f"資料不符合的欄位: {tmp_str.getvalue()}")
        else:
            result = user_data_auth_result(True, db_data)

        return result

    def check_process(self, request):      

        print(request.data)
        
        data_first_checked = self.format_check(request)

        if data_first_checked.get('code') == CodeMessageEnum.USER_AUTH_FAIL.value.get('code'):
            return data_first_checked

        data = data_first_checked.get('data')         

        if data.get('username') != "":            
            data_second_checked = self.check_by_specified_column(**{'username': data['username']})
        else:            
            data_second_checked = self.check_by_specified_column(**{'id_card': data['id_card']})

        if data_second_checked.get('code') == CodeMessageEnum.USER_AUTH_FAIL.value.get('code'):
            return data_second_checked
        else:
            member_data = data_second_checked.get('data')

        return self.third_check_other_column(member_data, data)


# 重設密碼
class ResetPasswordView(AuthUserInfo):

    def post(self, request):

        # 驗證程序
        data_pass_check = self.check_process(request)

        # 能否重製密碼
        if data_pass_check.get('code') == CodeMessageEnum.USER_AUTH_FAIL.value.get('code'):

            return Response(data_pass_check)

        else:
            member = data_pass_check.get('data')

            pwd = str()            
            for i in range(10):
                pwd = pwd + random.choice('abcdefghijklmnopqrstuvwxyz')

            member.set_password(pwd)
            member.save()

            result = user_data_auth_result(True, pwd)

            return Response(result)

# 解鎖


class UnlockView(AuthUserInfo):

    def post(self, request):

        # 驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check.get('data')

        # 能否解鎖
        if data_pass_check.get('code') == CodeMessageEnum.USER_AUTH_FAIL.value.get('code'):

            result = user_data_auth_result(False, None)

            return Response(result)
        else:            

            if member.is_lock:

                member.is_lock = False
                member.save()

                result = {"code": 11, "message": "已解鎖", "data": None}
                print("成功解鎖")
                return Response(res, status=status.HTTP_200_OK)
            else:
                res = {"code": 41, "message": "非鎖定狀態", "data": None}
                print("不須解鎖")
                return Response(res, status=status.HTTP_200_OK)

# 忘記帳號


class ForgetUserNameView(AuthUserInfo):

    def post(self, request, *args, **krgs):
        # 驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check['data']

        # 是否能回傳帳號
        if data_pass_check.get('code') == 10:

            res = {"code": 40, "message": "身分驗證錯誤", "data": None}

            return Response(res, status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 開始回傳帳號")
            res = {"code": 12, "message": "回傳帳號", "data": member.username}
            return Response(res, status=status.HTTP_200_OK)


# 查看開戶資訊
class CheckStatusView(AuthUserInfo):

    def post(self, request, *args, **krgs):
        # 通過驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check['data']

        # 是否回傳開戶資訊
        if data_pass_check.get('code') == 10:

            res = {"code": 40, "message": "身分驗證錯誤", "data": None}

            return Response(res, status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 開始回傳開戶資訊")
            res = {"code": 20, "message": "回傳開戶資料",
                   "data": member.has_open_account}

            return Response(res, status=status.HTTP_200_OK)


class LoginView(AuthUserInfo):

    queryset = Member.objects.all()
    serializer_class = LoginSerailizer

    # 登入程序進入點
    def post(self, request):        

        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            result = {"code": 100, "message": "帳密驗證錯誤", "data": serializer.errors}
            return Response(result, status=status.HTTP_200_OK)

        data = serializer.data

        # 驗證
        user0 = authenticate(request,
                             username=data['username'],
                             password=data['password'])

        # 帳號密碼正確
        if user0 is not None:

            # 取DB資料拿當前錯誤次數
            user = Member.objects.get(username=data['username'])

            result = errortime_hint(user.wrong_pwd_times)

            # 如果當前錯誤次數已不能登入
            if not result['can_login']:
                return Response(result, status=status.HTTP_200_OK)

            login(request, user0)
            print("登入成功")

            user.wrong_pwd_times = 0
            user.save()

            result = {"code": 101, "message": "登入成功", "data": ""}

            # 跳轉網頁
            return HttpResponseRedirect('/app1/index0/')

        # 帳密沒通過驗證
        else:

            # 確認是否有該帳號
            checked_data = self.check_by_specified_column(
                'username', data['username'])

            if checked_data['can_pass']:

                user = checked_data['data']
            else:

                return Response(checked_data, status=status.HTTP_200_OK)

            # 有該帳號後 => 提取錯誤次數
            wrong_pwd_times = user.wrong_pwd_times

            hint = errortime_hint(wrong_pwd_times)

            error_setting(user, wrong_pwd_times)

            return Response(hint, status=status.HTTP_200_OK)


# 跳轉頁面測試
def index0(request):
    try:
        user = Member.objects.get(username=request.user.username)
        return render(request, 'index.html', {"user": user, })
    except Member.DoesNotExist:
        return render(request, 'index.html', {})
    except Exception as e:
        return render(request, 'index.html', {})


# Week2 新增功能 =>錯誤次數設定
class ErrorSetting(APIView):

    def post(self, request):

        data = request.data

        serializers = Errortime_setting_serializer(data=data)

        if not serializers.is_valid(raise_exception=True):

            return Response("錯誤格式!", status=status.HTTP_200_OK)

        try:

            db_data = Errortimes.objects.get(
                name=serializers.data.get('name'))

            print(f"目前的錯誤和次數{db_data.name} : {db_data.value}")

            db_data.value = serializers.validated_data['value']

            print(f"更新後錯誤和次數{db_data.name} : {db_data.value}")

            db_data.save()

            return Response(f"更改成功! {db_data.name} 的次數更改成 {db_data.value}", status=status.HTTP_200_OK)

        except:

            # 如果輸入的變數名 是有支援的錯誤名稱 => 儲存改變
            if serializers.validated_data['name'] in ErrortimeEnum.__members__:

                serializers.save()

                return Response(f"新增成功!  {serializers.validated_data['name']} : {serializers.validated_data['value']}")

            else:

                return Response("目前不支援該錯誤對應的服務", status.HTTP_200_OK)

# 獲取目前該錯誤設定的次數


def errortime_getter(name):

    try:
        model = Errortimes.objects.get(name=name)

        return model.value
    except:
        #TODO 修改ENUM
        if name in ErrorSetting.__members__:
            return 10
        else:

            return None

# 錯誤次數提示


def errortime_hint(user_error_time):

    if user_error_time > errortime_getter('Cannot_use'):

        res = {"code": 110, "message": f"密碼錯誤超過上限，已無法使用",
               "data": "", "can_login": False}

    elif user_error_time > errortime_getter('Auto_ban'):

        res = {"code": 111, "message": f"密碼錯誤超過一定次數，已禁止",
               "data": "", "can_login": False}

    elif user_error_time > errortime_getter('Auto_lock'):

        res = {"code": 112, "message": f"密碼錯誤超過一定次數，已封鎖",
               "data": "", "can_login": False}

    else:

        res = {"code": 112, "message": "密碼錯誤 請重新登入",
               "data": "", "can_login": True}

    return res

# 對應錯誤次數的設定


def error_setting(user, error_times):
    if error_times >= errortime_getter('Cannot_use'):
        user.cannot_use = True
    elif error_times >= errortime_getter('Auto_ban'):
        user.is_ban = True
    elif error_times >= errortime_getter('Auto_lock'):
        user.is_lock = True

    user.wrong_pwd_times = user.wrong_pwd_times + 1

    user.save()


class MemberSignUp(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerailizer

    def post(self, request):
        """ 會員輸入註冊資料

        """
        data = request.data
        serializers = self.serializer_class(data=data)

        if not serializers.is_valid():
            return Response("資料格式錯誤", status=status.HTTP_200_OK)

        user = User.objects.create_user(username=serializers['username'],)

        return Response("會員註冊成功!", status=status.HTTP_200_OK)


def login_page(request):
    return render(request, 'login.html', {})


def user_data_auth_result(can_pass, data):
    """
    回傳用戶驗證後的結果字典
    """
    if can_pass:
        
        print("TEST-----------------------")
        print(CodeMessageEnum.USER_AUTH_FAIL.__doc__)
        print("TEST END-----------------------")

        code_message = CodeMessageEnum.get_result(20)

        result ={"code": code_message.get('code'),
                 "message": code_message.get('message'),
                 "data": data        
                }
    else :

        result ={"code": CodeMessageEnum.USER_AUTH_FAIL.value.get('code'),
                 "message": CodeMessageEnum.USER_AUTH_FAIL.value.get('message'),
                 "data": data        
                }
    
    return result
        
