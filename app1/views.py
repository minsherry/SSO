import random

from io import StringIO
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from enums.AuthStatusEnum import *
from enums.ErrorStrEnum import *
from .models import Errortimes, Member
from .serializers import *


class AuthUserInfo(GenericAPIView):
    '''
    用戶資料驗證程序
    '''

    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer

    def serializer_check(self, request):
        '''
        是否能通過serializer
        '''

        data = request.data
        serializer = self.serializer_class(data = data)

        if serializer.is_valid():
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, serializer.validated_data)
        else:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)

        return result

    def get_member_data_by_key_column(self, **column_name_and_value):
        '''
        根據關鍵欄位獲取 會員object
        '''

        try:
            member = Member.objects.get(**column_name_and_value)

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, member)

            return result

        except Exception:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)

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
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None, f"資料不符合的欄位: {tmp_str.getvalue()[:-1]}")
        else:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, memeber_data)

        return result

    def check_process(self, request):
        '''
        驗證程序起點
        '''

        print(request.data)

        data_serializer_check = self.serializer_check(request)
        
        if data_serializer_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:  # 如果沒通過序列化驗證
            return data_serializer_check

        data = data_serializer_check.get('data')

        if data.get('username') != "":  # 如果通過序列化驗證後的資料 沒有username
            data_key_column_checked = self.get_member_data_by_key_column(**{'username': data['username']})
        else:
            data_key_column_checked = self.get_member_data_by_key_column(**{'id_card': data['id_card']})
        
        if data_key_column_checked.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:  # 如果沒通過 關鍵欄位驗證
            return data_key_column_checked
        else:
            member_data = data_key_column_checked.get('data')

        result = self.other_column_check(member_data, data)  # 經過其餘欄位驗證後的結果

        return result


class ResetPasswordView(AuthUserInfo):
    '''
    用戶重置密碼
    '''

    def post(self, request):

        data_pass_check = self.check_process(request)  # 驗證程序
        
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:  # 能否重製密碼

            return Response(data_pass_check)

        else:
            member = data_pass_check.get('data')

            pwd = str()
            for i in range(10):
                pwd = pwd + random.choice('abcdefghijklmnopqrstuvwxyz')

            member.set_password(pwd)
            member.save()

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, pwd, "重製密碼成功!")

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
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.value.get('code'):

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)

            return Response(result)
        else:

            if member.is_lock:

                member.is_lock = False
                member.save()

                result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_UNLOCK_SUCCESS.code, None)

                return Response(result)
            else:
                result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_IS_NON_UNLOCK, None)

                return Response(result)


class ForgetUserNameView(AuthUserInfo):
    '''
    用戶忘記密碼
    '''

    def post(self, request):

        data_pass_check = self.check_process(request)

        member = data_pass_check.get('data')
        
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL:  # 是否能回傳帳號
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)
        else:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.RETURN_USER_ACCOUNT_NAME, member.username)

        return Response(result)


class CheckStatusView(AuthUserInfo):
    '''
    回傳用戶開戶資訊
    '''

    def post(self, request):        
        data_pass_check = self.check_process(request)  # 通過驗證程序

        member = data_pass_check['data']
        
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:  # 是否回傳開戶資訊
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)

            return Response(result)
        else:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.RETURN_USER_ACCOUNT_DATA.code, member.has_open_account)

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
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_DATA_FORMAT_ERROR, None)
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

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_SUCCESS, None)
            
            return HttpResponseRedirect('/app1/index0/')  # 跳轉網頁

        else:  # 帳密沒通過驗證

            checked_data = self.get_member_data_by_key_column(**{'username': data['username']})  # 確認是否有該帳號

            if checked_data.get('code') == CodeAndMessageEnum.USER_AUTH_SUCCESS.code:
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
        user = Member.objects.get(username=request.user.username)

        return render(request, 'index.html', {"user": user, })
    except Exception:
        return render(request, 'index.html')


def login_page(request):
    '''
    跳轉登入輸入html
    '''

    return render(request, 'login.html')


class ErrorSetting(APIView):
    '''
    登入失敗幾次會上鎖/禁止 的次數設定
    '''

    def put(self, request):

        data = request.data

        serializers = ErrortimeSettingSerializer(data = data)

        if not serializers.is_valid():

            return Response(CodeAndMessageEnum.DATA_FORMAT_ERROR.name)

        try:

            db_data = Errortimes.objects.get(name=serializers.validated_data.get('name'))

            db_data.value = serializers.validated_data.get('value')

            db_data.save()

            return Response(f"更改成功! {db_data.name} 的次數更改成 {db_data.value}")

        except:

            if serializers.validated_data.get('name') in ErrorNameEnum.__members__:
                serializers.save()

                return Response(f"新增成功!  {serializers.validated_data['name']} : {serializers.validated_data['value']}")

            else:

                return Response(CodeAndMessageEnum.SERVICE_NOT_EXISTED.message)


def get_errortime_set_now(error_name):
    '''
    獲取當前錯誤次數設定
    '''

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

    if user_error_time >= get_errortime_set_now(ErrorNameEnum.CANNOT_USE.name):
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_CANNNOT_USE.code, None)
    elif user_error_time >= get_errortime_set_now(ErrorNameEnum.AUTO_BAN.name):
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_BAN.code, None)
    elif user_error_time >= get_errortime_set_now(ErrorNameEnum.AUTO_LOCK.name):
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_LOCK.code, None)
    else:
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_FAIL.code, None)
    

    return result


def error_setting(user):
    '''
    依照用戶錯誤次數 設定帳戶上鎖或禁止    
    '''

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

    queryset = Member.objects.all()
    serializer_class = MemberSerailizer

    def post(self, request):

        data = request.data
        serializers = self.serializer_class(data = data)

        if serializers.is_valid():
            serializers.save()

            return Response(CodeAndMessageEnum.SIGN_UP_SUCCESS.message)
        else:
            return Response(CodeAndMessageEnum.SIGN_UP_DATA_FORMAT_ERROR.message)