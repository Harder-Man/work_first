import re

from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse
import json
from django.contrib.auth import login, authenticate, logout

from apps.users.utils import generic_user_id, check_user_id
from celery_tasks.emails.tasks import celery_send_email
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class UsernameCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


""" 注册功能视图 """


class RegisterView(View):
    def post(self, request):
        # 1. 接受请求
        body = request.body
        body_str = body.decode()
        data = json.loads(body_str)

        # 2. 提取参数
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')

        # 3. 验证参数
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '缺少关键参数'})

        # 3.1 验证用户名是否符合规则
        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足条件'})

        # 3.2 验证密码时候符合规则
        if not re.match('[a-zA-z0-9]{8,20}', password):
            return JsonResponse({'code': 400, 'errmsg': '您输入的密码格式不正确'})
        # 3.3 验证密码和确认密码是否一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码不一致'})
        # 3.4 验证手机号是否符合规则
        if not re.match('^1[345789]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '您输入的手机号格式不正确'})

        # 4. 保存数据到mysql
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)

        # 5. 状态保持
        request.session['id'] = user.id
        request.session['username'] = user.username
        request.session['mobile'] = user.mobile

        login(request, user)

        # 6. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class LoginView(View):
    def post(self, request):
        # 1. 接受请求数据
        data = json.loads(request.body.decode())

        # 2. 提取数据
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 3. 验证参数
        if not all([username, password, remembered]):
            return JsonResponse({'code': 400, 'errmsg': '数据不全'})

        # 4. 认证登录用户
        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errrmsg': '账号或密码错误'})

        # 5. 状态保持
        login(request, user)

        # 6. 要根据是否记住登录
        if remembered:
            request.session.set_expriy(None)
        else:
            request.session.set_expriy(0)

        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class LogoutView(View):
    def delete(self, request):
        # 删除session
        logout(request)

        # 删除cookie
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequiredJsonMixin, View):
    def get(self, request):
        user = request.user
        user_info = {'username': user.username,
                     'mobile': user.mobile,
                     'email': user.email,
                     'email_active': user.email_active
                     }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': user_info})


class EmailView(LoginRequiredJsonMixin, View):
    def put(self, request):
        data = json.loads(request.body.decode())

        email = data.get('email')
        user = request.user
        user.email = email
        user.save()

        token = generic_user_id(user.id)
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html'

        html_message = '<p>尊敬的用户您好！</p>'\
                        '<p>感谢您使用美多商城。</p>' \
                        '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                        '<p><a href="%s">%s<a></p>' % (email, verify_url,verify_url)

        celery_send_email.delay(email, html_message)

        return JsonResponse({"code": 0, 'errmsg': 'ok'})


class VerifyEmailView(View):
    def put(self, request):
        data = request.GET

        token = data.get('token')

        user_id = check_user_id(token)

        if user_id is None:
            return JsonResponse({"code":400})

        try:
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse({"code": 400})

        user.email_active=True
        user.save()

        return JsonResponse({'code':0, 'errmsg': 'ok'})
