import re
import json
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django_redis import get_redis_connection
from apps.oauth.utils import generic_openid, check_token
from django.contrib.auth import login

from apps.users.models import User


class QQUserView(View):
    def get(self, request):
        code = request.GET.get('code')

        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '缺少code参数'})

        # QQ登录参数
        QQ_CLIENT_ID = '101474184'
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

        """
        client_id = None        我们在创建应用的时候的 id
        client_secret = None    我们在创建爱你应用的时候的秘钥
        redirect_rui = None     当我们用户扫描同意之后,跳转的页面的url
        """
        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI)

        access_token = qq.get_access_token(code)

        openid = qq.get_open_id(access_token)

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except:
            token = generic_openid(openid)

            return JsonResponse({'code': 300, 'access_token': access_token})
        else:
            login(request, qquser.user)

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', qquser.user.username, max_age=14 * 24 * 3600)

        return response

    def post(self, request):

        data = json.loads(request.body.decode())

        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        openid = check_token(access_token)

        if not all([mobile, openid, password]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': '绑定失败'})

        if not re.match('1[3-9]\d{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的手机号'})

        if not re.match('[a-zA-Z0-9]{5,20}', password):
            return JsonResponse({'code': 400, 'errmsg': '密码不满足条件'})

        redis_cli = generic_openid('code')
        redis_sms_code = redis_cli.get(mobile)

        if sms_code != redis_sms_code.decode():
            return JsonResponse({'code': 490, 'errmsg': '短信验证码错误'})

        try:
            user = User.objects.get(mobile=mobile)
        except:
            user = User.objects.create_user(username=mobile,
                                            password=password,
                                            mobile=mobile)
        else:
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': ' 手机号或密码错误'})

            OAuthQQUser.objects.create(openid=openid, user=user)

            login(request, user)

            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', user.username, max_age=14 * 24 * 3360)

            return response
