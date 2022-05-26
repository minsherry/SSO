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
    '''
    用戶資料驗證程序
    '''

    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer
    
    def serializer_check(self, request):        

        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():            
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, serializer.validated_data)        
        else :                   
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)  

        return result
    
    def specified_column_check(self, **column_name_and_value):

        try:
            member = Member.objects.get(**column_name_and_value)            

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, member)                    

            return result

        except Exception:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)                    

            return result
    
    def other_column_check(self, memeber_data_in_db, request_data):    

        tmp_str = StringIO()

        if request_data.get('id_card') != memeber_data_in_db.id_card:            
            tmp_str.write("身分證 / ")

        if request_data.get('date_of_birth') != memeber_data_in_db.date_of_birth:            
            tmp_str.write("出生年月日 / ")

        if request_data.get('mobile_number') != memeber_data_in_db.mobile_number:
            tmp_str.write("連絡電話 / ")                 

        if tmp_str.getvalue():
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None, f"資料不符合的欄位: {tmp_str.getvalue()[:-1]}")        
        else:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_SUCCESS.code, memeber_data_in_db)

        print(result)

        return result

    def check_process(self, request):  
        
        data_first_checked = self.serializer_check(request)

        if data_first_checked.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:
            return data_first_checked

        data = data_first_checked.get('data')         

        if data.get('username') != "":            
            data_second_checked = self.specified_column_check(**{'username': data['username']})
        else:            
            data_second_checked = self.specified_column_check(**{'id_card': data['id_card']})

        if data_second_checked.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:
            return data_second_checked
        else:
            member_data = data_second_checked.get('data')

        result = self.other_column_check(member_data, data)

        return result

class ResetPasswordView(AuthUserInfo):
    '''
    用戶重置密碼
    '''

    def post(self, request):

        # 驗證程序
        data_pass_check = self.check_process(request)

        # 能否重製密碼
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:

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
        if data_pass_check.get('code') == CodeMessageEnum.USER_AUTH_FAIL.value.get('code'):

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

        member = data_pass_check['data']

        # 是否能回傳帳號
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL:
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.USER_AUTH_FAIL.code, None)            
        else:            
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.RETURN_USER_ACCOUNT_NAME, member.username)            

        return Response(result)

class CheckStatusView(AuthUserInfo):
    '''
    回傳用戶開戶資訊
    '''

    def post(self, request):
        # 通過驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check['data']

        # 是否回傳開戶資訊
        if data_pass_check.get('code') == CodeAndMessageEnum.USER_AUTH_FAIL.code:
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
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_DATA_FORMAT_ERROR, None)
            return Response(result)

        data = serializer.data

        # 驗證
        user0 = authenticate(request,
                             username=data.get('username'),
                             password=data.get('password'))

        # 帳號密碼正確
        if user0 is not None:

            # 取DB資料拿當前錯誤次數
            user = Member.objects.get(username=data.get('username'))

            result = errortime_hint(user.wrong_pwd_times)

            # 如果當前錯誤次數已不能登入
            if not result['can_login']:
                return Response(result)

            login(request, user0)
            print("登入成功")

            user.wrong_pwd_times = 0
            user.save()

            result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_SUCCESS, None)

            # 跳轉網頁
            return HttpResponseRedirect('/app1/index0/')

        # 帳密沒通過驗證
        else:

            # 確認是否有該帳號
            checked_data = self.specified_column_check(
                'username', data['username'])

            if checked_data['can_pass']:

                user = checked_data['data']
            else:

                return Response(checked_data)

            # 有該帳號後 => 提取錯誤次數
            wrong_pwd_times = user.wrong_pwd_times

            hint = errortime_hint(wrong_pwd_times)

            error_setting(user, wrong_pwd_times)

            return Response(hint)


# 跳轉頁面測試
def index0(request):
    try:
        user = Member.objects.get(username=request.user.username)
        return render(request, 'index.html', {"user": user, })
    except Member.DoesNotExist:
        return render(request, 'index.html', {})
    except Exception as e:
        return render(request, 'index.html', {})

class ErrorSetting(APIView):
    '''
    登入失敗幾次會上鎖/禁止 的次數設定
    '''

    def post(self, request):

        data = request.data

        serializers = ErrortimeSettingSerializer(data=data)

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
            
            if serializers.validated_data['name'] in ErrortimeEnum.__members__:

                serializers.save()

                return Response(f"新增成功!  {serializers.validated_data['name']} : {serializers.validated_data['value']}")

            else:

                return Response("目前不支援該錯誤對應的服務", status.HTTP_200_OK)


def errortime_getter(name):
    '''
    獲取用戶當前錯誤次數
    '''

    try:
        model = Errortimes.objects.get(name=name)

        return model.value
    except:
        #TODO 修改ENUM
        if name in ErrorSetting.__members__:
            return 10
        else:

            return None

def errortime_hint(user_error_time):   
    '''
    依照用戶錯誤次數給予相對應回傳結果
    '''

    if user_error_time > errortime_getter('Auto_ban'):
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_BAN.code, None)

    elif user_error_time > errortime_getter('Auto_lock'):        
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_LOCK.code, None)

    else:
        result = CodeAndMessageEnum.get_dict(CodeAndMessageEnum.LOGIN_FAIL.code, None)

    return result

def error_setting(user, error_times):
    '''
    依照用戶錯誤次數 設定帳戶上鎖或禁止
    '''
    
    if error_times >= errortime_getter('Auto_ban'):
        user.is_ban = True
    elif error_times >= errortime_getter('Auto_lock'):
        user.is_lock = True

    user.wrong_pwd_times = user.wrong_pwd_times + 1

    user.save()


class MemberSignUp(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerailizer

    def post(self, request):

        data = request.data
        serializers = self.serializer_class(data=data)

        if not serializers.is_valid():
            return Response(CodeAndMessageEnum.SIGN_UP_DATA_FORMAT_ERROR.message)

        # TODO
        # user = User.objects.create_user(username=serializers['username'],)

        return Response(CodeAndMessageEnum.SIGN_UP_SUCCESS.message)


def login_page(request):
    return render(request, 'login.html')      