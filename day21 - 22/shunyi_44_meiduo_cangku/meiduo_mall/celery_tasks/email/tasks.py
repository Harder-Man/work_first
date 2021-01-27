from django.core.mail import send_mail
from celery_tasks.main import app

@app.task
def celery_send_email(email,html_message):

    # subject, message, from_email, recipient_list,

    # subject,   主题
    subject = '美多商城激活邮件'

    # message,  邮件内容
    message = ''

    # from_email,   谁发的邮件
    from_email = '美多商城<qi_rui_hua@163.com>'

    # recipient_list,  收件人列表 ['邮箱','邮箱',,]
    recipient_list = [email]
    # recipient_list = [email,'qi_rui_hua@126.com']

    # 支持 HTML
    html_message = html_message #'<a href="http://www.meiduo.site:8080/index.html?user_id=1">点击激活</a>'

    send_mail(subject,
              message,
              from_email,
              recipient_list,
              html_message=html_message)
