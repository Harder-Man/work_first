import json
import re

from django.contrib.auth import login
from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse


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
