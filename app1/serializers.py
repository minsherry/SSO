from rest_framework import serializers
from app1.models import Errortimes, Member

class LoginSerailizer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Member
        fields = ('username', 'password')


class MemberSerailizer(serializers.ModelSerializer):
    '''
    會員註冊
    '''
    class Meta:
        model = Member
        fields = ('username', 'password', 'id_card', 'date_of_birth',
                  'mobile_number', 'first_name', 'last_name', 'email')

class ErrortimeSettingSerializer(serializers.ModelSerializer):
    '''
    錯誤次數設定
    '''

    class Meta:
        model = Errortimes
        fields = '__all__'

class IDVerifySerailizer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=True)
    id_card = serializers.CharField(max_length=10)

    class Meta:
        model = Member
        fields = ('username', 'id_card', 'date_of_birth', 'mobile_number')