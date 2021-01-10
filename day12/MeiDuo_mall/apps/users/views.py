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
