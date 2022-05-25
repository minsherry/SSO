import requests
import json
from app1.models import Member
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

class CheckMember():
    def identity_verify(self,data):        
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
        
        return {"is_correct_account":is_correct_account,"member":member}