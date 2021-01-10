import json
import re

# 设置session
from django.contrib.auth import login

from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse

# 验证用户账号和密码
from django.contrib.auth import authenticate


class UsernameCountView(View):

    # usernames/<username>/count/
    def get(self, request, username):
        # 1. 根据username进行数量的查询
        count = User.objects.filter(username=username).count()
        # 2. 将查询结果返回
        # code=0 表示成功

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class RegisterView(View):
    def post(self, request):
        """
        1.接收请求
        2.提取参数
        3.验证参数
        4.保存数据到MySQL
        5.状态保持(session redis)
        6.返回响应
        :param request:
        :return:
        """
        # 1.接收请求
        data = json.loads(request.body.decode())

        # 2.提取参数
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')

        # 3.验证参数
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': "参数不全"})

        if re.match('[a-zA-Z0-9_-]{8,20}', password):
            return JsonResponse({'code': 400, 'errmsg': '密码格式错误'})

        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码不一致'})

        if re.match('1[3|4|5|7|8][0-9]{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号格式错误'})

        # 4.保存数据到MySQL
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile)

        # 5.状态保持(session redis)
        login(request, user)
        # 6.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class LoginView(View):
    def post(self, request):
        """
        1.接收请求数据
        2.提取数据
        3.验证参数
        4.认证登录用户
        5.状态保持
        6.要根据是否记住登录(类似于 mail.163.com中的 10免登录 本质是设置session过期时间)
        7.返回响应
        :param request:
        :return:
        """
        # 1.接收请求数据
        data = json.loads(request.body.decode())

        # 2.提取数据
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 3.验证参数
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码不能为空'})

        if re.match('1[3|4|5|7|8][0-9]{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 4.认证登录用户
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})

        # 5.状态保持
        login(request, user)

        # 6.要根据是否记住登录(类似于 mail.163.com中的 10免登录 本质是设置session过期时间)
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', username, max_age=14 * 24 * 3600)

        # 7.返回响应
        return response
