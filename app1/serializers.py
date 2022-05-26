from rest_framework import serializers
from app1.models import Errortimes, Member

class LoginSerailizer(serializers.Serializer):
    
    username = serializers.CharField()
    password = serializers.CharField()       

class MemberSerailizer(serializers.ModelSerializer):
    '''
    會員註冊
    '''

    class Meta:
        model = Member
        fields = ('username', 'password', 'id_card', 'date_of_birth', 'mobile_number', 'first_name', 'last_name', 'email')

    def create(self, validated_data):
        '''
        Override Create 讓新增時就把密碼加密
        '''

        user = super(MemberSerailizer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class IDVerifySerailizer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=True)
    id_card = serializers.CharField(max_length=10)

    class Meta:
        model = Member
        fields = ('username', 'id_card', 'date_of_birth', 'mobile_number')


class ErrortimeSettingSerializer(serializers.Serializer):
    '''
    錯誤次數設定
    '''    

    name = serializers.CharField()
    value = serializers.IntegerField()

    def create(self, validated_data):
        return Errortimes.objects.create(**validated_data)