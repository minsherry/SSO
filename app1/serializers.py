from enum import unique
from app1.models import Member
from rest_framework import serializers

class LoginSerailizer(serializers.ModelSerializer):
    username = serializers.CharField()
    class Meta:
        model = Member
        fields = ('username','password')

class MemberSerailizer(serializers.ModelSerializer):
    class Meta:
        model=Member
        fields = '__all__'

class IDVerifySerailizer0(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=True)
    service_code = serializers.IntegerField()
    class Meta:
        model = Member
        fields = ('username','id_card','date_of_birth','mobile_number','service_code')

class IDVerifySerailizer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=True)
    id_card = serializers.CharField(max_length=10)
    class Meta:
        model = Member
        fields = ('username','id_card','date_of_birth','mobile_number')

class IDVerifyNoUNameSerailizer(serializers.ModelSerializer):
    id_card = serializers.CharField(max_length=10)
    class Meta:
        model = Member
        fields = ('id_card','date_of_birth','mobile_number')

class TestSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    message = serializers.CharField()

