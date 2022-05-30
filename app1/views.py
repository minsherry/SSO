from io import StringIO
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
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


        if serializer.is_valid():
            result = CodeNMsgEnum.USER_AUTH_SUCCESS.get_dict(serializer.validated_data)
        else:
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict()

        return result

    def member_obj_by_key_column(self, **column_name_and_value):
        '''
        根據關鍵欄位獲取 會員object
        '''

        try:
            member = Member.objects.get(**column_name_and_value)

            result = CodeNMsgEnum.USER_AUTH_SUCCESS.get_dict(member)

            return result

        except Exception:
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict()

            return result

    def other_column_check(self, memeber_data, request_data):
        '''
        其餘欄位資料驗證
        '''

        tmp_str = StringIO()

        #TODO change to for loop
        if request_data.get('id_card') != memeber_data.id_card:
            tmp_str.write("身分證 / ")

        if request_data.get('date_of_birth') != memeber_data.date_of_birth:
            tmp_str.write("出生年月日 / ")

        if request_data.get('mobile_number') != memeber_data.mobile_number:
            tmp_str.write("連絡電話 / ")

        if tmp_str.getvalue():
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict(None, f"資料不符合的欄位: {tmp_str.getvalue()[:-1]}")  # 回傳所有不符合的欄位名稱 && 去除掉最後的/
        else:
            result = CodeNMsgEnum.USER_AUTH_SUCCESS.get_dict(memeber_data)

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

        #  判斷式:  如果 request 的 username 去除空白後 是空字串 
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
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 不能重置密碼
            return Response(data_pass_check)

        else:  # 可以重置密碼
            member = data_pass_check.get('data')

            User = get_user_model()
            pwd = User.objects.make_random_password()  # 自動產生密碼

            member.set_password(pwd)
            member.save()

            result = CodeNMsgEnum.USER_AUTH_SUCCESS.get_dict(pwd, "密碼重置成功!")            

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
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict()

            return Response(result)
        else:
            if member.is_lock:
                member.is_lock = False
                member.save()

                result = CodeNMsgEnum.USER_UNLOCK_SUCCESS.get_dict()

                return Response(result)
            else:
                result = CodeNMsgEnum.USER_IS_NON_UNLOCK.get_dict()

                return Response(result)


class ForgetUserNameView(AuthUserInfo):
    '''
    用戶忘記密碼
    '''

    def post(self, request):

        data_pass_check = self.check_process(request)

        member = data_pass_check.get('data')
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 是否能回傳帳號
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict()
        else:
            result = CodeNMsgEnum.RETURN_USER_ACCOUNT_NAME.get_dict(member.username)

        return Response(result)


class CheckStatusView(AuthUserInfo):
    '''
    回傳用戶開戶資訊
    '''

    def post(self, request):        
        data_pass_check = self.check_process(request)  # 通過驗證程序

        member = data_pass_check.get('data')
        
        if data_pass_check.get('code') == CodeNMsgEnum.USER_AUTH_FAIL.code:  # 是否回傳開戶資訊
            result = CodeNMsgEnum.USER_AUTH_FAIL.get_dict()

            return Response(result)
        else:
            data = "True" if member.has_open_account else "False" # 志強那邊他設定是用CharFirld接 我直接傳bool會錯

            result = CodeNMsgEnum.RETURN_USER_ACCOUNT_DATA.get_dict(data)

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
            result = CodeNMsgEnum.LOGIN_DATA_FORMAT_ERROR.get_dict()

            return Response(result)        
        
        # 驗證用戶帳密
        auth_user = authenticate(request, username = serializer.validated_data.get('username'), password = serializer.validated_data.get('password'))  
        
        if auth_user is not None:  # 帳號密碼正確            
            user = Member.objects.get(username = serializer.validated_data.get('username'))  # 取DB資料拿當前錯誤次數

            result = errortime_hint(user.wrong_pwd_times)
            
            if result.get('data') == False:  # 如果當前錯誤次數已不能登入
                return Response(result)
            
            login(request, auth_user)            

            user.wrong_pwd_times = 0
            user.save()

            result = CodeNMsgEnum.LOGIN_SUCCESS.get_dict()
            
            return HttpResponseRedirect('/app1/login1/')  # 跳轉網頁

        else:  # 帳密沒通過驗證
            checked_data = self.member_obj_by_key_column(**{'username': data['username']})  # 確認是否有該帳號

            if checked_data.get('code') != CodeNMsgEnum.USER_AUTH_SUCCESS.code: # 沒有該帳號(程式斷點)
                return Response(checked_data)

            user = checked_data.get('data') # member obj在回傳字典中的data

            wrong_pwd_times = user.wrong_pwd_times  # 有該帳號後 => 提取錯誤次數

            hint = errortime_hint(wrong_pwd_times)            

            error_set(user)

            return Response(hint)


def page_after_login(request):
    '''
    登入後的畫面
    '''

    try:
        user = Member.objects.get(username = request.user.username) # 登入後的request中 就有user的資訊

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
    登入失敗幾次會上鎖/禁止 的次數設定, 這是提供給管理者自己看的
    '''

    def put(self, request):

        data = request.data

        serializers = ErrortimeSettingSerializer(data = data)

        if not serializers.is_valid():
            return Response(CodeNMsgEnum.DATA_FORMAT_ERROR.name)

        try:
            db_data = Errortimes.objects.get(**serializers.validated_data)

            result = f"錯誤次數更新成功! {db_data.name} 的次數更改成 {db_data.value}"

            return Response(result)

        except:
            if serializers.validated_data.get('name') in ErrorNameEnum.__members__: # 我要先確定這個name 是不是我應該提供的服務 
                serializers.save()

                result = f"錯誤新增成功!  {serializers.validated_data['name']} : {serializers.validated_data['value']}" 
            else:
                result = CodeNMsgEnum.SERVICE_NOT_EXISTED.message                

            return Response(result)


def get_errortime_set_now(error_name):
    '''
    獲取當前錯誤次數設定
    '''    
    error_default_value = ErrorNameEnum[error_name].value

    obj = Errortimes.objects.get_or_create(name = error_name, defaults={"name": error_name, "value": error_default_value})[0]

    return obj.value

def error_set(user):
    '''
    依照用戶錯誤次數 設定帳戶上鎖或禁止    
    ''' 
    
    if user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.CANNOT_USE.name):
        user.is_active_off
    elif user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.AUTO_BAN.name):
        user.is_ban_on
    elif user.wrong_pwd_times >= get_errortime_set_now(ErrorNameEnum.AUTO_LOCK.name):
        user.is_lock_on

    user.increase_errortime # 登入錯誤次數 + 1

    user.save()

def errortime_hint(user_error_time):
    '''
    依照用戶錯誤次數給予相對應回傳結果
    '''

    for set_time in ErrorNameEnum:

        if user_error_time > set_time.value: # 如果錯誤次數 > 設定次數 
            result = set_time.get_hint()
            break

        result = set_time.get_hint()  # 預設hint
    
    return result

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

            Member.objects.create_user(**serializers.validated_data)                        

            return Response(CodeNMsgEnum.SIGN_UP_SUCCESS.get_dict())
        else:
            return Response(CodeNMsgEnum.SIGN_UP_DATA_FORMAT_ERROR.message)

