from random import Random

from django.core.mail import EmailMessage, send_mail
from django.template import loader

from users.models import EmailVerifyRecord
from online_learning.settings import DEFAULT_FROM_EMAIL

def random_str(random_length=8):
    str = ''
    # 生成字符串的可选字符串
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type="register"):
    '''
    发送注册邮件
    :param email: 发给哪个邮箱
    :param send_type: 发送邮箱的目的是：注册或修改密码
    :return:
    '''
    # 发送之前先保存到数据库，到时候查询链接是否存在
    #  邮箱验证码model
    email_record = EmailVerifyRecord()
    # 生成随机的code放入链接
    code = random_str(16)
    email_record.code = code # 验证码
    email_record.email = email # 邮箱
    email_record.send_type = send_type # 发送类型：注册或找回密码
    email_record.save()

    # 定义邮件内容:
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "django - 注册激活链接"
        email_body = "邮箱已激活！"
        # "请点击下面的链接激活你的账号: http://127.0.0.1:8888/active/{0}".format(code)
        # 使用Django内置函数完成邮件发送。四个参数：主题，邮件内容，发件人邮箱地址，收件人（是一个字符串列表）
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email])
        # 如果发送成功
        if send_status:
            return True
        else:
            return False
    elif send_type == "forget":
        email_title = "django - 找回密码链接"
        email_body = loader.render_to_string(
            "email_forget.html",  # 需要渲染的html模板
            {
                "active_code": code  # 参数
            }
        )
        msg = EmailMessage(email_title, email_body, DEFAULT_FROM_EMAIL, [email])
        msg.content_subtype = "html"
        send_status = msg.send()
        # 如果发送成功
        if send_status:
            return True
        else:
            return False
    else:
        return False
