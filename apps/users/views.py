# encoding: utf-8
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse



class LoginView(View):
    '''用户登录'''
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html', {'msg': ''})

    def post(self, request, *args, **kwargs):
        user_name = request.POST.get('username', '')
        pass_word = request.POST.get("password", "")
        print(pass_word,1111111)

        # auth自带的验证用户的方法
        user = authenticate(username=user_name, password=pass_word)

        # 如果不是null说明验证成功
        if user is not None:
            login(request, user) # 将用户信息添加到session中
            # 跳转到首页 user request会被带回到首页
            return HttpResponseRedirect(reverse('index')) # reverse防止硬编码 直接用url中的name
            # 或者return HttpResponseRedirect('/')
        # 没有成功说明里面的值是None，并再次跳转回主页面
        else:
            return render(request, "login.html", {"msg": "用户名或密码错误!"})
