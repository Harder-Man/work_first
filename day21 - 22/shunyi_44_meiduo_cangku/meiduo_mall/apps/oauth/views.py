from django.shortcuts import render

# Create your views here.
"""
# 1. **获取code**，
# 2. **通过code换取access_token**，
# 3. **再通过access_token换取openid**
"""

from django.views import View
from django.http.response import JsonResponse

from QQLoginTool.QQtool import OAuthQQ

class QQUserView(View):

    def get(self,request):
        # 1. **获取code**，
        code=request.GET.get('code')
        if code is None:
            return JsonResponse({'code':400,'errmsg':'没有code参数'})

        # client_id = None,             我们在创建应用的时候的 id
        # client_secret = None,         我们在创建应用的时候的 秘钥
        # redirect_uri = None,          当我们用户扫描同意之后,跳转的页面的url
        # QQ登录参数

        # 我们申请的 客户端id
        QQ_CLIENT_ID = '101474184'
        # 我们申请的 客户端秘钥
        QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        # 我们申请时添加的: 登录成功后回调的路径
        QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI)

        # 2. **通过code换取access_token**，
        access_token=qq.get_access_token(code)

        # 3. **再通过access_token换取openid**
        openid=qq.get_open_id(access_token)
        # 'CBCF1AA40E417CD73880666C3D6FA1D6'


        # 4. 根据 openid 进行 数据查询
        from apps.oauth.models import OAuthQQUser
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果不存在 应该 返回 openid 让用户绑定

            # 注意!!!!!!!!!!!!!
            # code 必须是 300
            # 才会显示绑定页面

            # 对openid 进行加密
            from apps.oauth.utils import generic_openid
            token=generic_openid(openid)

            return JsonResponse({'code':300,'access_token':token})
        else:
            # 如果 存在 在进行自动登录(状态保持)操作
            # ① 状态保持
            from django.contrib.auth import login
            # login 的第二个参数 应该是 User 模型的实例对象
            # qquser.属性
            # OAuthQQUser 有 user 的属性
            login(request,qquser.user)
            # ② 设置cookie
            response = JsonResponse({'code':0,'errmsg':'ok'})

            # qquser.user  就是只的  User 的实例对象
            response.set_cookie('username',qquser.user.username,max_age=14*24*3600)

            return response


    def post(self,request):
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
        # 1. 接收参数  --JSON
        import json
        data = json.loads(request.body.decode())
        # 2. 提取参数
        mobile=data.get('mobile')
        password=data.get('password')
        sms_code=data.get('sms_code')
        access_token=data.get('access_token')

        #解密数据
        from apps.oauth.utils import check_token
        openid = check_token(access_token)
        if openid is None:
            return JsonResponse({'code':400,'errmsg':'绑定失败'})

        # 3. 验证参数 (省略--作业)
        #     3.0 mobile,password,sms_code,access_token(openid) 必须都有值
        #     3.1 手机号是否符合规则
        #     3.2 密码是否符合规格
        #     3.3 短信验证码是否正确

        # 4. 根据手机号判断用户信息
        from apps.users.models import User
        try:
            user=User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #     如果没有查询到,则新增一个用户
            # username 为什么 等于 mobile 因为绑定的时候 只让用户输入了手机号.我们就让 手机号和用户名 同名
            user=User.objects.create_user(username=mobile,
                                          mobile=mobile,
                                          password=password)
        else:
            #     如果查询到,则验证密码是否正确

            # user.check_password 是 父类的一个方法,系统为我们提供的 验证密码的方法
            if not user.check_password(password):
                #密码不正确,我们返回错误的响应
                return JsonResponse({'code':400,'errmsg':'绑定失败'})

        # 5. 绑定用户信息 (数据入库)
        from apps.oauth.models import OAuthQQUser
        OAuthQQUser.objects.create(openid=openid,user=user)
        # 6. 状态保持
        from django.contrib.auth import login
        login(request,user)

        # 7. 设置cookie
        response=JsonResponse({'code':0,'errmsg':'ok'})

        response.set_cookie('username',user.username,max_age=14*24*3600)

        # 8. 返回响应
        return response