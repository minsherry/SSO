import random

from io import StringIO
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from enums.AuthStatusEnum import *
from enums.ErrorStrEnum import *
from .models import Errortimes, Member
from .serializers import *

class AuthUserInfo(APIView):
    '''
    用戶資料驗證程序
    '''

    def serializer_check(self, request):
        '''
        是否能通過serializer
        '''

        data = request.data
        serializer = IDVerifySerailizer(data = data)

        member, created = Member.objects.get_or_create(
            id_num='A123456789',
            defaults={

            }
        )

        # update_or_create

        if serializer.is_valid():
            result = CodeNMsgEnum.USER_AUTH_SUCCESS.get_dict(serializer.validated_data)
        else:
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict(None)

        return result

    def member_obj_by_key_column(self, **column_name_and_value):
        '''
        根據關鍵欄位獲取 會員object
        '''

        try:
            member = Member.objects.get(**column_name_and_value)

            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_SUCCESS.code, member)

            return result

        except Exception:
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_FAIL.code, None)

            return result

    def other_column_check(self, memeber_data, request_data):
        '''
        其餘欄位資料驗證
        '''

        tmp_str = StringIO()

        if request_data.get('id_card') != memeber_data.id_card:
            tmp_str.write("身分證 / ")

        if request_data.get('date_of_birth') != memeber_data.date_of_birth:
            tmp_str.write("出生年月日 / ")

        if request_data.get('mobile_number') != memeber_data.mobile_number:
            tmp_str.write("連絡電話 / ")

        if tmp_str.getvalue():
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_FAIL.code, None, f"資料不符合的欄位: {tmp_str.getvalue()[:-1]}")
        else:
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_SUCCESS.code, memeber_data)

        return result

    def check_process(self, request):
        '''
        驗證程序起點
        '''        
        print(request.data)

        data_by_serializer = self.serializer_check(request)        
        
        if data_by_serializer.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 如果沒通過序列化驗證 (程式斷點)
            return data_by_serializer

        serializer_request = data_by_serializer.get('data') 

        #  如果 request 的 username 去除空白後 是空字串 
        data_by_key_column = self.member_obj_by_key_column(**{'username': serializer_request['username']}) if serializer_request.get('username').strip() else self.member_obj_by_key_column(**{'id_card': serializer_request['id_card']})
        
        if data_by_key_column.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 如果沒通過 關鍵欄位驗證 (程式斷點)
            return data_by_key_column
        
        member_obj = data_by_key_column.get('data')

        result = self.other_column_check(member_obj, serializer_request)  # 經過其餘欄位驗證後的結果

        return result

class ResetPasswordView(AuthUserInfo):
    '''
    用戶重置密碼
    '''

    def post(self, request):

        data_pass_check = self.check_process(request)  # 驗證程序
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 能否重製密碼
            return Response(data_pass_check)

        else:
            member = data_pass_check.get('data')

            pwd = Auth.

            

            for i in range(10):
                pwd = pwd + random.choice('abcdefghijklmnopqrstuvwxyz')

            member.set_password(pwd)
            member.save()

            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_SUCCESS.code, pwd, "重製密碼成功!")

            print(result)

            return Response(result)


class UnlockView(AuthUserInfo):
    '''
    用戶解鎖
    '''

    def post(self, request):

        # 驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check.get('data')

        # 能否解鎖
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.value.get('code'):
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_FAIL.code, None)

            return Response(result)
        else:
            if member.is_lock:
                member.is_lock = False
                member.save()

                result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_UNLOCK_SUCCESS.code, None)

                return Response(result)
            else:
                result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_IS_NON_UNLOCK, None)

                return Response(result)


class ForgetUserNameView(AuthUserInfo):
    '''
    用戶忘記密碼
    '''

    def post(self, request):

        data_pass_check = self.check_process(request)

        member = data_pass_check.get('data')
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL:  # 是否能回傳帳號
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_FAIL.code, None)
        else:
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.RETURN_USER_ACCOUNT_NAME, member.username)

        return Response(result)


class CheckStatusView(AuthUserInfo):
    '''
    回傳用戶開戶資訊
    '''

    def post(self, request):        
        data_pass_check = self.check_process(request)  # 通過驗證程序

        member = data_pass_check.get('data')
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 是否回傳開戶資訊
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.USER_AUTH_FAIL.code, None)

            return Response(result)
        else:
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.RETURN_USER_ACCOUNT_DATA.code, member.has_open_account)

            return Response(result)


class LoginView(AuthUserInfo):
    '''
    用戶登入
    '''

    queryset = Member.objects.all()
    serializer_class = LoginSerailizer

    def post(self, request):

        data = request.data
        serializer = self.serializer_class(data = data)

        if not serializer.is_valid():
            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_DATA_FORMAT_ERROR, None)
            return Response(result)

        data = serializer.data
        
        auth_user = authenticate(request, username = data.get('username'), password = data.get('password'))  # 驗證
        
        if auth_user is not None:  # 帳號密碼正確            
            user = Member.objects.get(username = data.get('username'))  # 取DB資料拿當前錯誤次數

            result = errortime_hint(user.wrong_pwd_times)
            
            if result.get('data') == False:  # 如果當前錯誤次數已不能登入
                return Response(result)
            
            login(request, auth_user)            

            user.wrong_pwd_times = 0
            user.save()

            result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_SUCCESS, None)
            
            return HttpResponseRedirect('/app1/login1/')  # 跳轉網頁

        else:  # 帳密沒通過驗證
            checked_data = self.member_obj_by_key_column(**{'username': data['username']})  # 確認是否有該帳號

            if checked_data.get('code') == CodeNMsgEnum.USER_AUTH_SUCCESS.code:
                user = checked_data.get('data')
            else:
                return Response(checked_data)

            wrong_pwd_times = user.wrong_pwd_times  # 有該帳號後 => 提取錯誤次數

            hint = errortime_hint(wrong_pwd_times)            

            error_setting(user)

            return Response(hint)


def page_after_login(request):
    '''
    登入後的畫面
    '''

    try:
        user = Member.objects.get(username = request.user.username)

        return render(request, 'index.html', {"user": user})
    except Exception:
        return render(request, 'index.html')


def login_page(request):
    '''
    跳轉登入輸入html
    '''

    return render(request, 'login.html')

def log_out(request):
    '''
    登出
    '''

    logout(request)
    return HttpResponseRedirect('/app1/login/')

class ErrorSetting(APIView):
    '''
    登入失敗幾次會上鎖/禁止 的次數設定
    '''

    def put(self, request):

        data = request.data

        serializers = ErrortimeSettingSerializer(data = data)

        if not serializers.is_valid():
            return Response(CodeNMsgEnum.DATA_FORMAT_ERROR.name)

        try:
            db_data = Errortimes.objects.get(**serializers.validated_data)

            return Response(f"更改成功! {db_data.name} 的次數更改成 {db_data.value}")

        except:
            if serializers.validated_data.get('name') in ErrorNameEnum.__members__:
                serializers.save()

                return Response(f"新增成功!  {serializers.validated_data['name']} : {serializers.validated_data['value']}")

            else:
                return Response(CodeNMsgEnum.SERVICE_NOT_EXISTED.message)


def get_errortime_set_now(error_name):
    '''
    獲取當前錯誤次數設定
    '''
    #TODO 改掉這個怪東西
    try:
        model = Errortimes.objects.get(name = error_name)        

        return model.value
    except:
        if error_name in ErrorNameEnum.__members__:
            return ErrorNameEnum.DEFAULT.value
        else:
            return ErrorNameEnum.DEFAULT.value


def errortime_hint(user_error_time):
    '''
    依照用戶錯誤次數給予相對應回傳結果
    '''

    #TODO 換成迴圈寫法
    if user_error_time >= get_errortime_set_now(ErrorNameEnum.CANNOT_USE.name):
        result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_CANNNOT_USE.code, None)
    elif user_error_time >= get_errortime_set_now(ErrorNameEnum.AUTO_BAN.name):
        result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_BAN.code, None)
    elif user_error_time >= get_errortime_set_now(ErrorNameEnum.AUTO_LOCK.name):
        result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_LOCK.code, None)
    else:
        result = CodeNMsgEnum.get_dict(CodeNMsgEnum.LOGIN_FAIL.code, None)   

    return result

def error_setting(user):
    '''
    依照用戶錯誤次數 設定帳戶上鎖或禁止    
    '''

    #TODO 換成迴圈寫法
    if user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.CANNOT_USE.name):
        user.is_active = False
    elif user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.AUTO_BAN.name):
        user.is_ban = True
    elif user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.AUTO_LOCK.name):
        user.is_lock = True

    user.wrong_pwd_times = user.wrong_pwd_times + 1  # 登入錯誤次數 + 1

    user.save()

class MemberSignUp(GenericAPIView):
    '''
    會員註冊
    '''
    
    #TODO Response不要寫死 && 只傳一個字串
    queryset = Member.objects.all()
    serializer_class = MemberSerailizer

    def post(self, request):

        data = request.data
        serializers = self.serializer_class(data = data)

        if serializers.is_valid():
            serializers.save()

            return Response(CodeNMsgEnum.SIGN_UP_SUCCESS.get_dict())
        else:
            return Response(CodeNMsgEnum.SIGN_UP_DATA_FORMAT_ERROR.message)

