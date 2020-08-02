# encoding: utf-8
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from users.forms import LoginForm, RegisterForm


class LoginView(View):
    '''用户登录'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        return render(request, 'login.html', {'msg': ''})

    def post(self, request, *args, **kwargs):
        # 使用LoginForm验证从表单提交的信息是否符合LoginForm中的规定
        login_form  = LoginForm(request.POST)
        # 如果验证成功，才校验用户的账号密码是否正确
        if login_form.is_valid():
            user_name = login_form.cleaned_data['username']
            pass_word = login_form.cleaned_data['password']

            # auth自带的验证用户的方法
            user = authenticate(username=user_name, password=pass_word)

            # 如果不是null说明验证成功
            if user is not None:
                login(request, user)  # 将用户信息添加到session中
                # 跳转到首页 user request会被带回到首页
                return HttpResponseRedirect(reverse('index'))  # reverse防止硬编码 直接用url中的name
                # 或者return HttpResponseRedirect('/')
            # 没有成功说明里面的值是None，并再次跳转回主页面
            else:
                # 用户验证失败
                return render(request, "login.html", {"msg": "用户名或密码错误!"})
        else:
            # 表单验证失败 可能是密码不符合required=True, min_length=6
            error_msg = {"login_form": login_form}
            return render(request, "login.html", error_msg)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        # 从request中获取访问当前视图的url，也就是说，退出后重新刷新下当前页面
        current_url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(current_url)

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        # 访问注册界面，需要返回图片验证码
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form': register_form})