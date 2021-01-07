from django.core.mail import send_mail
from Celery_tasks.main import app


@app.task
def celery_send_email(email, html_message):
    # subject, message, from_mail, recipient_list,
    # subject = '主题'
    subject = '美多商城'
    # message = '邮件内容'
    message = ''
    from_mail = '美多商城<qi_rui_hua@163.com>'
    recipient_list = [email]



    send_mail(subject,
              message,
              from_mail,
              recipient_list,
              html_message=html_message)