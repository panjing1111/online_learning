"""online_learning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from organization.views import OrgView
from users.views import LoginView, LogoutView, RegisterView, ForgetPwdView, ResetView, ModifyPwdView

import xadmin

urlpatterns = [
    path('admin/', xadmin.site.urls),
    # 验证码url
    path("captcha/", include('captcha.urls')),
    # TemplateView.as_view会将template转换为view
    path('', TemplateView.as_view(template_name='index.html'), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    # 将主路由和子路由绑定
    # path('users/', include('users.urls')),  # 已经匹配到了users这个位置
    # 忘记密码
    path('forget/', ForgetPwdView.as_view(), name="forget_pwd"),
    # 重置密码
    re_path('reset/(?P<active_code>.*)/?', ResetView.as_view(), name="reset_pwd"),
    # 修改密码url; 用于passwordreset页面提交表单
    path('modify_pwd/', ModifyPwdView.as_view(), name="modify_pwd"),

    # 课程机构首页url
    path('org_list/', OrgView.as_view(), name="org_list"),

]
