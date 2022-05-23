import requests
import json

from optparse import BadOptionError
from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.shortcuts import render
from .models import Post

from .serializers import PostSerializer,TestSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db import transaction


def hello_world(request):
    print("hhhh")
    for data in request:
        print(data)
    return render(request, 'hello_world.html', {'current_time': str(datetime.now()), })


def try_some(request):
    return HttpResponse('{"one":1,"two":"22"}')

def test0(request):
    r =requests.get('http://127.0.0.1:9487/try/')
    d=r.text
    #print(json.loads(r))
    # rr=r.json
    # print(rr.status_code)
    return HttpResponse(d)

def test1(request):
    r =requests.get('https://jsonplaceholder.typicode.com/users')
    r=r.text
    data = json.loads(r)
    for d in data:
        op = op+d
    #print(json.loads(r))
    # rr=r.json
    # print(rr.status_code)
    return HttpResponse(op)

def test2(request):
    return render(request,'test2.html',{})


def home(request):
    post_list = Post.objects.all()
    print("000000")
    return render(request, 'home.html', {
        'post_list': post_list,
        'type': str(type(123)),
    })


def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return HttpResponse("can't found")
    except:
        pass
    return render(request, 'post.html', {'post': post})

class PostView(GenericAPIView):
    qureyset = Post.objects.all()
    serializer_class = TestSerializer
    """
    def get(self,request,*args,**krgs):

        '''
        users = self.get_queryset()
        serializer = self.serializer_class(users,many=True)
        data=serializer.data
        return JsonResponse(safe=False)
        '''
        a=request.GET.get('a')
        return Response(f'i see you {a}')
    """
    def post(self,request,*args,**krgs):
        data=request.data
        try:
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            data=serializer.data

            c=data['opInt']
        except Exception as e:
            data = {'error':str(e)}
        #return JsonResponse(data)
        return HttpResponse(data.keys())

        

# def abc(name, gend="f", age=10):
#     pass

# abc("Anna", 30)
