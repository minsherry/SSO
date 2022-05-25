from django.urls import path
from .views import *

urlpatterns = [
    path('resetpwd/', ResetPasswordView.as_view(), name='resetpwd'),
    path('unlock/', UnlockView.as_view()),
    path('forgetusername/', ForgetUserNameView.as_view()),
    path('checkaccount/', CheckStatusView.as_view()),
    path('login/', LoginPage, name='login_page'),
    path('login0/', LoginView.as_view(), name="loginEx"),
    path('index0/', index0),
    path('error_setting/', ErrorSetting.as_view()),
    path('member_sign_up', MemberSignUp.as_view())
]
