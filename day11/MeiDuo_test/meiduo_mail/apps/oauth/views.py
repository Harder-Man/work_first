import json

from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from django.contrib.auth import login
from apps.oauth.models import OAuthQQUser
from django.http.response import JsonResponse

from apps.oauth.utils import generic_openid, check_openid
from apps.users.models import User


class QQUserView(View):
    def get(self, request):
        # 1. 获取code
        code = request.GET.get('code')
        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '没有code参数'})

        QQ_CLIENT_ID = '101474184'
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI)

        # 2. 通过 coke 换取 token
        access_token = qq.get_access_token(code)

        # 3. 通过 token 获取 openid
        openid = qq.get_open_id(access_token)

        # 4. 根据 openid 进行数据查询
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            token = generic_openid(openid)
            return JsonResponse({'code': 300, 'access_token': token})
        else:
            login(request, qquser.user)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', qquser.user.username, max_age=14 * 24 * 3600)

        return response

    def post(self, request):

        # 1. 接收参数
        data = json.loads(request.body.decode())

        # 2. 提取参数
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        openid = check_openid(access_token)
        # 3. 验证参数

        # 4. 根据手机号判断用户信息
        try:
            user = User.objects.get(mobile=mobile)
        except:
            user = User.objects.create(username=mobile,
                                       password=password,
                                       mobile=mobile)
        else:
            if not user.check_password(password):
                return JsonResponse({"code": 400, 'errmsg': '绑定失败'})

        # 5. 绑定用户信息
        OAuthQQUser.objects.create(openid=openid, user=user)
        login(request, user)

        response = JsonResponse({'code':0, 'errmsg':'ok'})
        response.set_cookie('username', user.username, max_age=14*24*3600)

        return response

