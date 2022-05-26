from django.urls import path
from .views import *

urlpatterns = [
    path('resetpwd/', ResetPasswordView.as_view(), name ='resetpwd'),
    path('unlock/', UnlockView.as_view()),
    path('forgetusername/', ForgetUserNameView.as_view()),
    path('checkaccount/', CheckStatusView.as_view()),
    path('login/', login_page, name ='login_page'),
    path('login0/', LoginView.as_view(), name ="loginEx"),
    path('login1/', page_after_login),  
    path('error_setting/', ErrorSetting.as_view()),  #當前 鎖定/禁止 次數設定
    path('member_sign_up', MemberSignUp.as_view()),  #會員註冊
]
