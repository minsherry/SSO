from rest_framework import serializers
from app1.models import Errortimes, Member


class LoginSerailizer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Member
        fields = ('username', 'password')


class MemberSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('username', 'password', 'id_card', 'date_of_birth',
                  'mobile_number', 'first_name', 'last_name', 'email')


class IDVerifySerailizer(serializers.ModelSerializer):
    username = serializers.CharField(allow_blank=True)
    id_card = serializers.CharField(max_length=10)

    class Meta:
        model = Member
        fields = ('username', 'id_card', 'date_of_birth', 'mobile_number')

# 錯誤次數設定
class Errortime_setting_serializer(serializers.Serializer):

    name = serializers.CharField()
    value = serializers.IntegerField()

    # 實作create
    def create(self, validated_data):
        return Errortimes.objects.create(**validated_data)

# 會員開戶資料
# class Member_data_serilaizer(serializers.Serializer):
