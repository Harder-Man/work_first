from celery_tasks.main import app
from django.core.mail import send_mail
from apps.users.utils import generic_user_id

@app.task
def celery_send_email(email, html_message):
    subject = '美多商城激活邮件'

    message = ''

    from_email = '美多商城<qi_rui_hua@163.com>'

    recipient_list = [email]

    verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token = % s'% token

    html_message = html_message

    send_mail(subject,
              message,
              from_email,
              recipient_list,
              html_message = html_message)
