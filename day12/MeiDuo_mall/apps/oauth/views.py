import re
import json
from django.views import View
from apps.users.models import User
from django.contrib.auth import login
from django.http.response import JsonResponse
from django_redis import get_redis_connection

# 导入qq包
from QQLoginTool.QQtool import OAuthQQ
from apps.oauth.models import OAuthQQUser

# 加密和解密
from apps.oauth.utils import *


class QQUserView(View):
    def get(self, request):
        """
        1. 获取code
        2. 通过code换取access_token
        3. 通过access_token换取openid
        4. 根据openid进行数据查询
        5. 如果不存在 进行注册
        6. 如果存在 保存session
        7. 设置cookie
        8. 返回响应

        :param request:
        :return:
        """
        # 1. 获取code
        code = request.GET.get('code')

        if code is None:
            return JsonResponse({'code': 400, 'errmsg': '没有code参数'})

        QQ_CLIENT_ID = '101474184'
        # 我们申请的 客户端秘钥
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        # 我们申请时添加的: 登录成功后回调的路径
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI)

        # 2. 通过code换取access_token
        access_token = qq.get_access_token(code)

        # 3. 通过access_token换取openid
        openid = qq.get_open_id(access_token)

        # 4. 根据openid进行数据查询
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except:
            # 5. 如果不存在 进行注册
            token = generic_openid(openid)
            return JsonResponse({'code': 300, 'access_token': token})
        else:
            # 6. 如果存在 保存session
            login(request, qquser.user)

        # 7. 设置cookie
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', qquser.user.username, max_age=14 * 24 * 3600)

        # 8. 返回响应
        return response

    def post(self, request):
        """
        1. 接收参数
        2. 提取参数
        3. 验证参数 (省略--作业)
        3.0 mobile,password,sms_code,access_token(openid) 必须都有值
        3.1 手机号是否符合规则
        3.2 密码是否符合规格
        3.3 短信验证码是否正确
        4. 根据手机号判断用户信息
        如果没有查询到,则新增一个用户
        如果查询到,则验证密码是否正确
        5. 绑定用户信息
        6. 状态保持
        7. 设置cookie
        8. 返回响应
        :param request:
        :return:
        """
        # 1. 接收参数
        data = json.loads(request.body.decode())
        # 2. 提取参数
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        openid = check_token(access_token)

        # 3. 验证参数 (省略--作业)
        # 3.0 mobile,password,sms_code,access_token(openid) 必须都有值
        if not all([mobile, password, sms_code, openid]):
            return JsonResponse({"code": 400, 'errmsg': '参数不全'})

        # 3.1 手机号是否符合规则
        if not re.match('1[3|4|5|7|8][0-9]{9}', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号格式错误'})

        # 3.2 密码是否符合规格
        if not re.match('[a-zA-Z0-9_-]{8,20}', password):
            return JsonResponse({'code': 400, 'errmsg': '密码格式错误'})

        # 3.3 短信验证码是否正确
        redis_cli = get_redis_connection('code')
        redis_sms_code = redis_cli.get(mobile)
        if sms_code != redis_sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码错误'})
        # 4. 根据手机号判断用户信息
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 如果没有查询到,则新增一个用户
            user = User.objects.create_user(name=mobile,
                                            password=password,
                                            mobile=mobile)
        else:
            # 如果查询到,则验证密码是否正确
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '绑定错误'})

        # 5. 绑定用户信息
        OAuthQQUser.objects.create(openid=openid, user=user)

        # 6. 状态保持
        login(request, user)

        # 7. 设置cookie
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)

        # 8. 返回响应
        return response
