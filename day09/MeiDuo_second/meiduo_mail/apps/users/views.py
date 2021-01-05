import re

from django.contrib.auth import login
from django.shortcuts import render

# Create your views here.
from django.views import View
import json
from django.http.response import JsonResponse

from apps.users.models import User

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
