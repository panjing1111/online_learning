# encoding: utf-8
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from users.forms import LoginForm, RegisterForm, ForgetForm, ActiveForm, ModifyPwdForm
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
            # 注册完成后登录
            login(request, user_profile)  # 将用户信息添加到session中
            # 跳转到登录页面
            return HttpResponseRedirect(reverse('index'))  # reverse防止硬编码 直接用url中的name
        # 注册邮箱form验证失败
        else:
            return render(request, "register.html", {"register_form": register_form})


# 用户忘记密码的处理view
class ForgetPwdView(View):
    '''这个是在登录界面的 忘记密码接口'''
    # get方法直接返回页面
    def get(self, request):
        # 给忘记密码页面加上验证码
        active_form = ActiveForm(request.GET)
        return render(request, "forgetpwd.html", {"active_form": active_form})
    # post方法实现
    def post(self, request):
        forget_form = ForgetForm(request.POST)
        # form验证合法情况下取出email
        if forget_form.is_valid():
            email = forget_form.cleaned_data["email"]

            # 首先查看数据库中是否能找到这个邮箱
            if UserProfile.objects.get(email=email):
                # 发送找回密码邮件
                send_register_email(email, "forget")
                # 发送完毕返回登录页面并显示发送邮件成功。
                return render(request, "login.html", {"msg":"重置密码邮件已发送,请注意查收"})
            else:
                # 瞎输的一个邮箱。
                return render(request, "login.html", {"msg": "邮箱未注册"})
        # 如果表单验证失败也就是他验证码输错等。
        else:
            return render(request, "forgetpwd.html", {"forget_from": forget_form })

# 重置密码的view  由于重置密码的时候携带active_code，将ResetView与ModifyPwdView分开写
class ResetView(View):
    '''用户邮箱会收到一个链接、打开这个链接输入新密码'''
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        # 如果不为空也就是有用户
        active_form = ModifyPwdForm(request.GET)
        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 将email传回来
                return render(request, "password_reset.html", {"email":email})
        # 自己瞎输的active_code
        else:
            return render(
                request, "forgetpwd.html", {
                    "msg": "您的重置密码链接无效,请重新请求", "active_form": active_form})


class ModifyPwdView(View):
    def post(self, request):
        modiypwd_form = ModifyPwdForm(request.POST)
        if modiypwd_form.is_valid():
            pwd1 = modiypwd_form.cleaned_data["password1"]
            pwd2 = modiypwd_form.cleaned_data["password2"]
            email = modiypwd_form.cleaned_data["email"]
            # 如果两次密码不相等，返回错误信息
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致"})
            # 如果密码一致
            user = UserProfile.objects.get(email=email)
            # 加密成密文
            user.password = make_password(pwd2)
            # save保存到数据库
            user.save()
            return render(request, "login.html", {"msg": "密码修改成功，请登录"})
        # 验证失败说明密码位数不够。
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modiypwd_form": modiypwd_form})
