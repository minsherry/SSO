
from django.contrib import admin
from django.urls import path, include
from .views import (
                        MemberView,
                        test_json,
                        test_get_json,
                        IdentityVerificationView,
                        ResetPasswordView,
                        UnlockView,
                        ForgetUnameView,
                        CheckStatusView,
                        index0,
                        LoginView,
                        LoginPage
                    )
urlpatterns =[
    path('',MemberView.as_view()),
    path('testjson/',test_json),
    path('testgetjson/',test_get_json),
    path('trypost/',IdentityVerificationView.as_view()),
    path('resetpwd/',ResetPasswordView.as_view(),name='resetpwd'),
    path('unlock/',UnlockView.as_view()),
    path('forgetusername/',ForgetUnameView.as_view()),
    path('checkaccount/',CheckStatusView.as_view()),
    #進入登入畫面
    path('login/',LoginPage),
    #執行登入動作/判斷
    path('login0/',LoginView.as_view(),name="loginEx"),
    #登入後跳轉的頁面
    path('index0/',index0)
]