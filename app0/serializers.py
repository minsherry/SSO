from app0.models import Post
from rest_framework import serializers

from app1.models import Member

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title','location')

class TestSerializer(serializers.Serializer):
    opChar = serializers.CharField()
    opInt = serializers.IntegerField()
    opBool  = serializers.BooleanField()
