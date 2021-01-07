import re
import json
from django.views import View
from apps.users.models import User
from utils.views import LoginRequireJsonMixin
from django.contrib.auth import login, logout
from django.http.response import JsonResponse
from apps.users.utils import generic_user_id, check_user_id


#
class UserNamesView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


#
#
# class MobileView(View):
#     def get(self, request, mobile):
#         count = User.objects.filter(mobile=mobile).count()
#         return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class JsonData(View):
    def post(self, request):
        # 1. 接收数据
        body = request.body
        body_str = body.decode()
        data = json.loads(body_str)

        # 2. 提取数据
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')

        # 3. 验证数据
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '缺少关键数据'})

        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名格式错误'})

        if not re.match('[a-zA-Z0-9_-]{8,25}', password):
            return JsonResponse({'code': 400, 'errmsg': '密码格式错误'})

        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码不一致'})

        if not re.match('^1[345789]\d{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号码格式错误'})

        # 4. 保存数据
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)

        # 5. 设置session
        request.session['id'] = user.id
        request.session['username'] = user.username
        # request.session['password'] = user.password
        request.session['mobile'] = user.mobile
        login(request, user)

        # 6. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class LoginView(View):
    def post(self, request):

        data = json.loads(request.body.decode())

        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        if not all([username, password]):
            return JsonResponse({'code': 400, 'errrmsg': '账号或密码不能为空'})

        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '账号或密码错误'})

        login(request, user)

        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', username, 14 * 24 * 3600)

        return response


class LogoutView(View):
    def delete(self, request):
        logout(request)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequireJsonMixin, View):
    def get(self, request):
        user = request.user

        user_info = {
            'username': user.username,
            'mobile': user.mobile,
            'email': user.email,
            'email_active': False
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': user_info})


class EmailView(LoginRequireJsonMixin, View):
    def put(self, request):
        data = json.loads(request.body.decode())

        email = data.get('email')

        if email is None:
            return JsonResponse({'code': 400, 'errmsg': '邮箱不能为空'})

        if re.match('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return JsonResponse({'code': 400, 'errmsg': '邮箱格式错误'})

        user = request.user
        user.email = email
        user.save()

        token = generic_user_id(user.id)

        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token

        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        from Celery_tasks.emails.tasks import celery_send_email

        celery_send_email.delay(email, html_message)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class VerifyEmailView(View):
    def put(self, request):

        token = request.GET.get('token')

        user_id = check_user_id(token)

        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '链接失效'})

        try:
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '用户不存在'})

        user.email_active = True

        user.save()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
