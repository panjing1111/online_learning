from django import forms

# 引入验证码field
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    # 用户名与密码不能为空
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    # 用户名不能小于5位
    username = forms.CharField(required=True, min_length=5)
    # 此处email与前端name需保持一致。
    email = forms.EmailField(required=True)
    # 密码不能小于5位
    password = forms.CharField(required=True, min_length=5)
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

# 忘记密码实现
class ForgetForm(forms.Form):
    # 此处email与前端name需保持一致。
    email = forms.EmailField(required=True)
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

# 激活时验证码实现
class ActiveForm(forms.Form):
    # 激活时不对邮箱密码做验证
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

# 重置密码form实现
class ModifyPwdForm(forms.Form):
    email = forms.EmailField(required=True)
    # 密码不能小于5位
    password1 = forms.CharField(required=True, min_length=5)
    # 密码不能小于5位
    password2 = forms.CharField(required=True, min_length=5)