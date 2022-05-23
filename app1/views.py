import re
import requests
import json
import random

from urllib import response
from django.shortcuts import render
# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import    (LoginSerailizer,
                            MemberSerailizer,
                            TestSerializer,
                            IDVerifySerailizer,
                            IDVerifySerailizer0,
                            IDVerifyNoUNameSerailizer)
from .models import Member
from datetime import datetime
from django.http import Http404, HttpRequest,HttpResponse,HttpResponseBadRequest, HttpResponseRedirect,JsonResponse
from django.contrib import auth
from http import HTTPStatus
from sre_parse import State
from defs.check_member import CheckMember
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect

class MemberView(GenericAPIView):
    qureyset = Member.objects.all()
    serializer_class = LoginSerailizer

    def get(self,request,*args,**krgs):
        a = request.GET.get('a')
        return Response(f'i see you {a}',200)

    def post(self,request,*args,**krgs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response("格式錯誤",200)
        data= serializer.data
        return Response(data)
        

def test_json(request):
    data ={"food":"apple","drink":"coffee",
           "num":1024,"ID":"S123456789"}
    return JsonResponse(data)

def test_get_json(request):
    url='http://10.66.200.52:9487/app1/testjson/'
    response = requests.get(url)
    data = response.text
    print(str(type(data)))
    jdata = json.loads(data)
    drink = jdata['drink']
    return HttpResponse(drink)

#測試資料
class IdentityVerificationView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer0

    def post(self,request,*args,**krgs):
        #驗證資料格式
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(f"填入的格式錯誤\
            {data}",status=status.HTTP_200_OK)
        print("格式正確")
        data = serializer.data
        
        #傳資料給另一個server
        url = "http://10.66.200.53:8000/Managers/password/"
        payload = json.dumps({
            "id_card":data["id_card"],
            "date_of_birth":data["date_of_birth"],
            "mobile_number":data["mobile_number"],
            "service_code":data["service_code"]
        })
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.status_code)

        #判斷回傳的資料
        if response.status_code != 200:
            return Response(f"無法連線客服端\n{response.status_code}",status=status.HTTP_200_OK)

        #response=response
        r=json.loads(response.text)
        test = TestSerializer(data=r)
        if not test.is_valid():
            return Response("回傳資料錯誤{r}",status=status.HTTP_200_OK)

        data0 = test.data

        return Response(data0,status=status.HTTP_200_OK)

#重設密碼
class ResetPasswordView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer

    def post(self,request,*args,**krgs):
        print("start respwd")
        #驗證資料格式
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            print("格式不正確")
            res={"code":43,"message":"輸入格式錯誤","data":serializer.errors}
            return Response(res,status=status.HTTP_200_OK)
        print("格式正確")
        data = serializer.data
        #驗證身分
        is_correct_account = True
        #以帳號查詢
        if data['username'] !="":
            #嘗試是否有帳號
            try:
                member = Member.objects.get(username=data['username'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not member.id_card == data['id_card']:
                print(f"{member.id_card}\t{data['id_card']}")
                is_correct_account=False
                print("id_card is not correct")
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not  member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")
            if not is_correct_account:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
        #以身分證查詢
        else:
            try:
                member = Member.objects.get(id_card=data['id_card'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")


        #重置密碼
        if not is_correct_account:
            res={"code":40,"message":"身分驗證錯誤","data":None}
            return Response(res,status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 嘗試重置密碼")
            pwd=str()
            for i in range(10):
                pwd =pwd+random.choice('abcdefghijklmnopqrstuvwxyz')
            member.set_password(pwd)
            print(pwd)
            print(member.check_password(pwd))
            member.save()
            res={"code":10,"message":"已重置密碼","data":pwd}
            return Response(res,status=status.HTTP_200_OK)

#解鎖
class UnlockView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer

    def post(self,request,*args,**krgs):
        #驗證資料格式
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            print("格式不正確")
            res={"code":43,"message":"輸入格式錯誤","data":serializer.errors}
            return Response(res,status=status.HTTP_200_OK)
        print("格式正確")
        data = serializer.data

        #驗證身分
        is_correct_account = True
        #以帳號查詢
        if data['username'] !="":
            #嘗試是否有帳號
            try:
                member = Member.objects.get(username=data['username'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not member.id_card == data['id_card']:
                print(f"{member.id_card}\t{data['id_card']}")
                is_correct_account=False
                print("id_card is not correct")
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not  member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")
            if not is_correct_account:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
        #以身分證查詢
        else:
            try:
                member = Member.objects.get(id_card=data['id_card'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")

        #被鎖住,操作解鎖
        if not is_correct_account:
            res={"code":40,"message":"身分驗證錯誤","data":None}
            return Response(res,status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 嘗試解鎖")
            if member.is_lock:
                member.is_lock=False
                member.save()
                res={"code":11,"message":"已解鎖","data":None}
                print("成功解鎖")
                return Response(res,status=status.HTTP_200_OK)
            else:
                res={"code":41,"message":"非鎖定狀態","data":None}
                print("不須解鎖")
                return Response(res,status=status.HTTP_200_OK)

#忘記帳號
class ForgetUnameView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = IDVerifyNoUNameSerailizer

    def post(self,request,*args,**krgs):
        #驗證資料格式
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            print("格式不正確")
            res={"code":43,"message":"輸入格式錯誤","data":serializer.errors}
            return Response(res,status=status.HTTP_200_OK)
        print("格式正確")
        data = serializer.data

        #驗證身分
        is_correct_account = True
        #以身分證查詢        
        try:
            member = Member.objects.get(id_card=data['id_card'])
        except Member.DoesNotExist:
            res={"code":40,"message":"身分驗證錯誤0","data":None}
            return Response(res,status=status.HTTP_200_OK)
        except:
            res={"code":42,"message":"非預期錯誤","data":None}
            return Response(res,status=status.HTTP_200_OK)

        #如果身分正確
        if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
            print(f"{member.date_of_birth}\t{data['date_of_birth']}")
            is_correct_account=False
            print("date_of_birth is not correct")
        if not member.mobile_number == data['mobile_number']:
            print(f"{member.mobile_number}\t{data['mobile_number']}")
            is_correct_account=False
            print("mobile_number is not correct")
        
        #回傳帳號
        if not is_correct_account:
            res={"code":40,"message":"身分驗證錯誤1","data":None}
            return Response(res,status=status.HTTP_200_OK)
        else:
            print("身分驗證成功 開始回傳帳號")
            res={"code":12,"message":"回傳帳號","data":member.username}
            return Response(res,status=status.HTTP_200_OK)

#查看開戶資訊
class CheckStatusView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = IDVerifySerailizer

    def post(self,request,*args,**krgs):
        #驗證資料格式
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            print("格式不正確")
            res={"code":43,"message":"輸入格式錯誤","data":serializer.errors}
            return Response(res,status=status.HTTP_200_OK)
        print("格式正確")
        data = serializer.data

        #驗證身分
        is_correct_account = True
        #以帳號查詢
        if data['username']!="":
            #嘗試是否有帳號
            try:
                member = Member.objects.get(username=data['username'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤0","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not member.id_card == data['id_card']:
                print(f"{member.id_card}\t{data['id_card']}")
                is_correct_account=False
                print("id_card is not correct")
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not  member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")
            if not is_correct_account:
                res={"code":40,"message":"身分驗證錯誤1","data":None}
                return Response(res,status=status.HTTP_200_OK)
        #以身分證查詢
        else:
            try:
                member = Member.objects.get(id_card=data['id_card'])
            except Member.DoesNotExist:
                res={"code":40,"message":"身分驗證錯誤","data":None}
                return Response(res,status=status.HTTP_200_OK)
            except Exception as e:
                res={"code":42,"message":"非預期錯誤","data":e}
                return Response(res,status=status.HTTP_200_OK)

            #如果身分正確
            if not  member.date_of_birth == datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date():
                print(f"{member.date_of_birth}\t{data['date_of_birth']}")
                is_correct_account=False
                print("date_of_birth is not correct")
            if not member.mobile_number == data['mobile_number']:
                print(f"{member.mobile_number}\t{data['mobile_number']}")
                is_correct_account=False
                print("mobile_number is not correct")
        
        #顯示是否開戶
        if not is_correct_account:
            res={"code":40,"message":"身分驗證錯誤","data":None}
            return Response(res,status=status.HTTP_200_OK)
        else:    
            print("身分驗證成功 開始回傳開戶資訊")  
            res={"code":20,"message":"回傳開戶資料","data":member.has_open_account}
            return Response(res,status=status.HTTP_200_OK)

#登入頁面
def LoginPage(request):
    return render(request,'login.html',{})

#登入 TODO 需要移到另一個app
class LoginView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = LoginSerailizer

    # @csrf_protect
    def post(self,request,*args,**krgs):
        print("start login post")
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():            
            res={"code":100,"message":"帳密驗證錯誤","data":serializer.errors}
            return Response(res,status=status.HTTP_200_OK)        
        data = serializer.data
        print(f"serializer data => {data}")

        #以下可以做帳號的密碼錯誤

        try:
            user = Member.objects.get(username = data["username"])
        except Member.DoesNotExist:
            res={"code":101,"message":"沒有該帳號","data":""}
            print("沒有該帳號")
            # return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={"code":102,"message":"其他錯誤","data":e}
            print(f"其他錯誤:{e}")
            # return Response(res,status=status.HTTP_200_OK)

        print("start try login")

        user0 = authenticate(request,
                            username=data['username'], 
                            password=data['password'])

        #帳號密碼正確
        if user0 is not None:   
            if user.wrong_pwd_times >3:
                res={"code":110,"message":"密碼錯誤超過3次，已封鎖","data":""}
                return Response(res,status=status.HTTP_200_OK)
            login(request,user0)
            print("登入成功")
            user.wrong_pwd_times=0
            user.save()
            res={"code":101,"message":"登入成功","data":""}
            #跳轉網頁
            return HttpResponseRedirect('/app1/index0/')
        #帳密沒通過驗證
        else:
            #有該帳號
            if user is not None:
                if user.wrong_pwd_times >3:
                    user.wrong_pwd_times=user.wrong_pwd_times+1
                    user.save()
                    res={"code":110,"message":"密碼錯誤超過3次，已封鎖","data":""}
                    return Response(res,status=status.HTTP_200_OK)

                # if not check_password(data["password"], user.password):
                user.wrong_pwd_times=user.wrong_pwd_times+1
                user.save()
                print(f"{user.username}密碼錯誤+1")

            print("登入失敗")
            res={"code":102,"message":"登入失敗","data":""}
            return Response(res,status=status.HTTP_200_OK)
    

#跳轉頁面測試
def index0(request):
    try:
        user = Member.objects.get(username = request.user.username)
        return render(request,'index.html',{"user":user,})
    except Member.DoesNotExist:
        return render(request,'index.html',{})    
    except Exception as e:
        return render(request,'index.html',{})    