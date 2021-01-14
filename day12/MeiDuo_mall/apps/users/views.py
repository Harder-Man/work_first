import json
import re

# 设置session
from django.contrib.auth import login, logout

from django.views import View

from apps.goods.models import SKU
from apps.users.models import User
from django.http.response import JsonResponse

# 验证用户账号和密码
from django.contrib.auth import authenticate

# 验证用户是否登录
from utils.views import LoginRequiredJsonMixin

# 异步发送邮件
from celery_tasks.email_tasks.tasks import celery_send_email

# 加密和解密
from apps.users.utils import *

# 导入地址模块
from apps.users.models import Address

# 链接redis
from django_redis import get_redis_connection


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

        if not re.match('[a-zA-Z0-9]{8,20}', password):
            return JsonResponse({'code': 400, 'errmsg': '密码格式错误'})

        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码不一致'})

        if not re.match('1[3|4|5|7|8][0-9]{9}', mobile):
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


class LogoutView(View):
    def delete(self, request):
        # 1. 删除session
        logout(request)

        # 2. 删除cookie
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')

        # 3. 返回响应
        return response


class UserInfoView(LoginRequiredJsonMixin, View):
    def get(self, request):
        """
        1. 判断 必须是登录用户
        2. 获取用户信息
        3. 返回响应
        :param request:
        :return:
        """
        # 1. 判断 必须是登录用户
        # 2. 获取用户信息
        user = request.user

        user_info = {
            'username': user.username,
            'mobile': user.mobile,
            'email': user.email,
            'email_active': user.email_active
        }

        # 3. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': user_info})


class EmailView(LoginRequiredJsonMixin, View):

    def put(self, request):
        """
        1. 判断用户是否登录
        2. 接收请求
        3. 提取参数
        4. 验证参数(省略--作业)
        5. 更新用户信息(数据入库)
        6. 发送激活邮件(下一节讲)
        7. 返回响应
        :param request:
        :return:
        """
        # 1. 判断用户是否登录
        # 2. 接收请求
        data = json.loads(request.body.decode())
        # 3. 提取参数
        email = data.get('email')
        # 4. 验证参数(省略--作业)

        # 5. 更新用户信息(数据入库)
        user = request.user
        user.email = email
        user.save()

        # 6. 发送激活邮件(下一节讲)
        token = generic_user_id(user.id)
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token = % s' % token
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        celery_send_email.delay(email, html_message)

        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class VerifyEmailView(View):

    def put(self, request):
        """
        1. 接收请求
        2. 提取数据
        3. 对数据进行解密操作
        4. 判断有没有user_id
        5. 如果没有则说明 token过期了
        6. 如果有,则查询用户信息
        7. 改变用户的邮箱激活状态
        8. 返回响应
        :param request:
        :return:
        """
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 提取数据
        token = data.get('token')

        # 3. 对数据进行解密操作
        user_id = check_user_id(token)
        # 4. 判断有没有user_id
        if user_id is None:
            # 5. 如果没有则说明 token过期了
            return JsonResponse({'code': 400, 'errmsg': '链接失效'})
        try:
            # 6. 如果有,则查询用户信息
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '用户不存在'})

        # 7. 改变用户的邮箱激活状态
        user.email_active = True
        user.save()

        # 8. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class CreateAddressView(View):

    def post(self, request):
        """
        1. 必须是登录用户才可以新增地址
        2. 接收参数
        3. 提取参数
        4. 验证参数 (省略--作业)
        5. 数据入库
        6. 返回响应
        :param request:
        :return:
        """
        # 1. 必须是登录用户才可以新增地址
        data = json.loads(request.body.decode())

        # 3. 提取参数(课件copy)
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        # 4. 验证参数 (省略--作业)
        # 5. 数据入库
        address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        # 6. 返回响应
        address_dict = {
            'id': address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})


class AddressListView(LoginRequiredJsonMixin, View):
    def get(self, request):
        """
        1. 必须是登录用户才可以获取地址
        2. 根据用户信息查询地址信息
        3. 需要对查询结果集进行遍历, 转换为字典列表
        4. 返回响应
        :param request:
        :return:
        """
        # 1. 必须是登录用户才可以获取地址
        # 2. 根据用户信息查询地址信息
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 3. 需要对查询结果集进行遍历, 转换为字典列表
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })

        # 4. 返回响应
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'addresses': addresses_list,
                             'default_address_id': request.user.default_address_id})


class UserHistoryView(LoginRequiredJsonMixin, View):

    def post(self, request):
        """
        0. 必须是登录用户
        1. 接收请求
        2. 提取参数
        3. 验证参数
        4. 连接redis
        5. 去重数据
        6. 添加数据
        7. 最多保存5条记录
        8. 返回响应
        :param request:
        :return:
        """
        # 1. 接收请求
        data = json.loads(request.body.decode())

        # 2. 提取参数
        sku_id = data.get('sku_id')

        # 3. 验证参数
        try:
            SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        # 4. 连接redis
        redis_cli = get_redis_connection('history')

        # 5. 去重数据
        redis_cli.lrem(request.user.id, 0, sku_id)

        # 6. 添加数据
        redis_cli.lpush(request.user.id, sku_id)

        # 7. 最多保存5条记录
        redis_cli.ltrim(request.user.id, 0, 4)

        # 8. 返回响应
        return JsonResponse({"code": 0, 'errmsg': 'ok'})

    def get(self, request):
        """
        1. 必须是登录用户
        2. 获取用户信息
        3. 连接redis
        4. 查询浏览记录 [1,2,3]
        5. 遍历列表数据,查询商品详细信息
        6. 将对象转换为字典数据
        7. 返回响应
        :param request:
        :return:
        """
        # 1. 必须是登录用户
        # 2. 获取用户信息
        user = request.user

        # 3. 连接redis
        redis_cli = get_redis_connection('history')

        # 4. 查询浏览记录 [1,2,3]
        sku_id = redis_cli.lrange(user.id, 0, -1)

        # 5. 遍历列表数据,查询商品详细信息
        skus = []
        for id in sku_id:
            sku = SKU.objects.get(id=id)
            # 6. 将对象转换为字典数据

            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        # 7. 返回响应
        return JsonResponse({"code": 0, 'errmsg': 'ok', 'skus': skus})
