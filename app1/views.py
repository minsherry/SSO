import random
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from enums.Errortime_enum import errortime_enum
from .models import Errortimes, Member
from .serializers import *

# Week2 重構 => BaseClass


class AuthUserInfo(GenericAPIView):

    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer

    # 資料格式驗證
    def auth_data_format(self, request):

        # 驗證資料格式
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            res = {"code": 43, "message": "輸入格式錯誤",
                   "data": serializer.errors, "can_pass": False}
            return res

        res = {"code": 40, "message": "輸入格式正確",
               "data": serializer.validated_data, "can_pass": True}

        return res

    # 關鍵資料欄位是否存在 (傳入要get的欄位名稱 和 對應值)
    def is_column_existed(self, column_name, value):

        try:
            kw = {f"{column_name}": f"{value}"}

            member = Member.objects.get(**kw)

            res = {"code": 40, "message": f"{column_name} Check Pass",
                   "data": member, "can_pass": True}

            return res

        except Member.DoesNotExist:

            res = {"code": 40, "message": "身分驗證錯誤",
                   "data": None, "can_pass": False}

            return res

        except Exception as e:

            res = {"code": 42, "message": "非預期錯誤",
                   "data": e, "can_pass": False}

            return res

    # 會員其他欄位資料是否相符合
    def data_column_check(self, member, data):

        # 會有不需要傳id_card進來的狀況
        if 'id_card' in data and not member.id_card == data['id_card']:

            res = {"code": 43, "message": "id_card is not correct",
                   "data": None, "can_pass": False}

        elif not member.date_of_birth == data['date_of_birth']:

            res = {"code": 44, "message": "date_of_birth is not correct",
                   "data": None, "can_pass": False}

        elif not member.mobile_number == data['mobile_number']:

            res = {"code": 45, "message": "mobile_number is not correct",
                   "data": None, "can_pass": False}

        else:

            res = {"code": 40, "message": "All check pass",
                   "data": member, "can_pass": True}

        return res

    # 驗證程序
    def check_process(self, request):
        # 檢查格式
        data_format_checked = self.auth_data_format(request)

        print(f"data_format_checked => {data_format_checked['can_pass']}")

        if not data_format_checked['can_pass']:
            return data_format_checked

        data = data_format_checked['data']

        # 如果username是空的
        if 'username' in data and data['username'] != "":
            data_column_checked = self.is_column_existed(
                'username', data['username'])

        else:
            data_column_checked = self.is_column_existed(
                'id_card', data['id_card'])

        print(f"data_column_checked =>  {data_column_checked['can_pass']}")

        if not data_column_checked['can_pass']:
            return data_column_checked

        else:
            member = data_column_checked['data']

        return self.data_column_check(member, data)


# 重設密碼
class ResetPasswordView(AuthUserInfo):

    def post(self, request, *args, **krgs):

        # 驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check['data']

        # 能否重製密碼
        if not data_pass_check['can_pass']:

            res = {"code": 40, "message": "身分驗證錯誤", "data": None}

            return Response(res, status=status.HTTP_200_OK)

        else:
            print("身分驗證成功 嘗試重置密碼")
            pwd = str()
            for i in range(10):
                pwd = pwd+random.choice('abcdefghijklmnopqrstuvwxyz')
            member.set_password(pwd)
            print(pwd)
            print(member.check_password(pwd))
            member.save()
            res = {"code": 10, "message": "已重置密碼", "data": pwd}
            return Response(res, status=status.HTTP_200_OK)

# 解鎖


class UnlockView(AuthUserInfo):

    def post(self, request, *args, **krgs):

        # 驗證程序
        data_pass_check = self.check_process(request)

        member = data_pass_check['data']

        # 能否解鎖
        if not data_pass_check['can_pass']:

            res = {"code": 40, "message": "身分驗證錯誤", "data": None}

            return Response(res, status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 嘗試解鎖")
            if member.is_lock:
                member.is_lock = False
                member.save()
                res = {"code": 11, "message": "已解鎖", "data": None}
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
        if not data_pass_check['can_pass']:

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
        if not data_pass_check['can_pass']:

            res = {"code": 40, "message": "身分驗證錯誤", "data": None}

            return Response(res, status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 開始回傳開戶資訊")
            res = {"code": 20, "message": "回傳開戶資料",
                   "data": member.has_open_account}
            return Response(res, status=status.HTTP_200_OK)

# 登入頁面


def LoginPage(request):
    return render(request, 'login.html', {})

# 登入


class LoginView(AuthUserInfo):

    queryset = Member.objects.all()
    serializer_class = LoginSerailizer

    # 登入程序進入點
    def post(self, request, *args, **krgs):
        print("start login post")

        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            res = {"code": 100, "message": "帳密驗證錯誤", "data": serializer.errors}
            return Response(res, status=status.HTTP_200_OK)

        data = serializer.data

        # 驗證
        user0 = authenticate(request,
                             username=data['username'],
                             password=data['password'])

        # 帳號密碼正確
        if user0 is not None:

            # 取DB資料拿當前錯誤次數
            user = Member.objects.get(username=data['username'])

            res = errortime_hint(user.wrong_pwd_times)

            # 如果當前錯誤次數已不能登入
            if not res['can_login']:
                return Response(res, status=status.HTTP_200_OK)

            login(request, user0)
            print("登入成功")

            user.wrong_pwd_times = 0
            user.save()

            res = {"code": 101, "message": "登入成功", "data": ""}

            # 跳轉網頁
            return HttpResponseRedirect('/app1/index0/')

        # 帳密沒通過驗證
        else:

            # 確認是否有該帳號
            checked_data = self.is_column_existed('username', data['username'])

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
                name=serializers.validated_data['name'])

            print(f"目前的錯誤和次數{db_data.name} : {db_data.value}")

            db_data.value = serializers.validated_data['value']

            print(f"更新後錯誤和次數{db_data.name} : {db_data.value}")

            db_data.save()

            return Response(f"更改成功! {db_data.name} 的次數更改成 {db_data.value}", status=status.HTTP_200_OK)

        except:

            # 如果輸入的變數名 是有支援的錯誤名稱 => 儲存改變
            if serializers.validated_data['name'] in errortime_enum.__members__:

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
        # 如果Db沒資料 傳回當前預設值
        if name in errortime_enum.__members__:

            return errortime_enum[name].value

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

# 會員註冊


class MemberSignUp(GenericAPIView):

    queryset = Member.objects.all()
    serializer_class = MemberSerailizer

    # 輸入會員註冊資料
    def post(self, request):

        data = request.data
        serializers = self.serializer_class(data=data)

        if not serializers.is_valid(raise_exception=True):
            return Response("資料格式錯誤", status=status.HTTP_200_OK)

        serializers.save()

        self.encryption_password(serializers.validated_data['username'])

        return Response("會員註冊成功!", status=status.HTTP_200_OK)

    # 密碼取出加密
    def encryption_password(self, username):

        member = Member.objects.get(username=username)

        member.set_password(member.password)

        member.save()

# # 會員登入查詢
# @method_decorator(login_required)
# class Member_data(GenericAPIView):

#     # queryset = Member_data.objects.get()
