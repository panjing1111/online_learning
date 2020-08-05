# encoding: utf-8
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from users.forms import LoginForm, RegisterForm
from users.models import UserProfile, EmailVerifyRecord
from utils.email_send import send_register_email

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

    def post(self, request):
        # 实例化form
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():

            user_name = register_form.cleaned_data["username"]
            # user_name是唯一的，因此可以用username查询是否新用户
            if UserProfile.objects.filter(username=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户名已经被使用"})

            user_email = register_form.cleaned_data["email"]
            if UserProfile.objects.filter(email=user_email):
                return render(request, "register.html", {"register_form": register_form, "msg": "邮箱已被注册过"})

            pass_word = register_form.cleaned_data["password"]
            # 实例化一个user_profile对象，将前台值存入
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_email
            user_profile.password = make_password(pass_word) # 密码加密
            # 发送注册激活邮件
            send_email_result = send_register_email(user_email, "register")
            if send_email_result:
                user_profile.save()

            # 跳转到登录页面
            return render(request, "index.html", )
        # 注册邮箱form验证失败
        else:
            return render(request, "register.html", {"register_form": register_form})

