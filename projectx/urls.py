"""projectx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app0.views import hello_world, try_some, home, post_detail,test0,test1,test2
from django.views.generic.base import TemplateView # 新增

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/',include('django.contrib.auth.urls')),
    path('hello/', hello_world),
    path('try/', try_some),
    path('test0/', test0),
    path('test1/', test1),
    path('', home),
    path('<int:pk>/', post_detail, name='post_detail'),
    path('app0/',include('app0.urls')),
    path('app1/',include('app1.urls')),
    #path('account/',include('account.urls')),
    #path('', TemplateView.as_view(template_name='home.html')), # 新增
    path('test2/',test2,name='test2')

    
]