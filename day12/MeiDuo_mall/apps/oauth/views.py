from django.contrib.auth import login
from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse

# 导入qq包
from QQLoginTool.QQtool import OAuthQQ
from apps.oauth.models import OAuthQQUser

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
            return JsonResponse({'code':400, 'errmsg':'没有code参数'})

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
            return JsonResponse({'code': 300, 'access_token': openid})
        else:
            # 6. 如果存在 保存session
            login(request, qquser.user)

        # 7. 设置cookie
        response = JsonResponse({'code': 0 , 'errmsg': 'ok'})
        response.set_cookie('username', qquser.user.username, max_age=14*24*3600)

        # 8. 返回响应
        return response