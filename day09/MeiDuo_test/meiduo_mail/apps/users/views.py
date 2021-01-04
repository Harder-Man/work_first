import re

from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse
import json
from django.contrib.auth import login


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
