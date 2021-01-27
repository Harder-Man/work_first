from django.shortcuts import render

# Create your views here.

from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse

class UsernameCountView(View):

    # usernames/<username>/count/
    def get(self,request,username):

        # 1. 根据username进行数量的查询
        count=User.objects.filter(username=username).count()
        # 2. 将查询结果返回
        # code=0 表示成功
        return JsonResponse({'code':0,'errmsg':'ok','count':count})


#####################注册功能视图###############################################
import json
import re

class RegisterView(View):

    def post(self,request):

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
        # 前端是将JSON数据以POST方式传递过来的
        # request.GET       1
        # request.POST      2
        # request.body      3
        body=request.body                   # request.body 是bytes类型的数据
        body_str=body.decode()              # bytes转 str
        data = json.loads(body_str)         # str 转 dict

        # 2.提取参数
        username=data.get('username')
        password=data.get('password')
        password2=data.get('password2')
        mobile=data.get('mobile')
        allow=data.get('allow')

        # 3.验证参数(主要是 思想.以后去公司写代码的时候 必须要添加)
        # 3.1 提取的5个变量 都必须有值
        # all([xxx,xxx,xxx])
        # all([]) 列表中的变量 只有有一个数据为None,整个 all() 表达式的值就是False

        if not all([username,password,password2,mobile,allow]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        # 3.2 验证用户名是否符合规则
        if not re.match('[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名不满足条件'})
        # 3.3 验证密码是否符合规则 (作业)
        # 3.4 验证密码和确认密码一致 (作业)
        # 3.5 验证手机号是否符合规格 (作业)

        # 4.保存数据到MySQL
        """
        >>> book = BookInfo(
        ...         name='python入门',
        ...         pub_date='2010-1-1'
        ...     )
        >>> book.save()
        
        >>> PeopleInfo.objects.create(
        ...         name='itheima',
        ...         book=book
        ...     )

        """
        # user=User(username=username,password=password,mobile=mobile)
        # user.save()

        # user=User.objects.create(username=username,password=password,mobile=mobile)

        # 以上2种方式都可以, 但是以上2中方式都有一个问题!!!
        # 密码没有加密

        # create_user 是django 认证系统提供的方法
        # 这个方法 可以对 用户的密码进行加密操作
        user=User.objects.create_user(username=username,
                                      password=password,
                                      mobile=mobile)

        # 5.状态保持(session redis) 单独讲
        # 设置session的基本操作
        # request.session['id']=user.id
        # request.session['username']=user.username
        # request.session['mobile']=user.mobile


        # django 自带后台 -- 后台也是采用的 session技术
        # django 实现了 session状态保持
        from django.contrib.auth import login

        # 参数1: request      请求对象
        # 参数2: user         用户信息
        login(request,user)

        # 6.返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})

##################################################################
# 登录

class LoginView(View):

    def post(self,request):
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
        username=data.get('username')
        password=data.get('password')
        remembered=data.get('remembered')


        # 应该在这里改
        # 我们根据 username 的值 来判断
        if re.match('1[3-9]\d{9}',username):
            # 如果username 的值为 手机号,我们进行mobile的判断
            User.USERNAME_FIELD='mobile'
        else:
            # 如果username 的值不为手机号,我们进行username的判断
            User.USERNAME_FIELD='username'

        # 3.验证参数
        # 用户名和密码是必须要传递的!!!
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        # 3.1 用户名规格(作业)
        # 3.2 密码规格(作业)
        # 4.认证登录用户
        # django 自带 admin后台. admin 可以验证用户名和密码
        # django 实现了 用户名和密码的验证方法
        from django.contrib.auth import authenticate

        # authenticate 把用户名和密码传递过去之后,会帮助我们验证 用户名和密码是否正确
        # 如果正确,则返回 username对应的 模型对象
        # 如果不正确,则返回 None

        # 设置关键字参数
        user=authenticate(username=username,password=password)

        if user is None:
            # user is None 说明 用户名或密码不正确
            # 我们千万不要告诉 前端 准确的错误信息
            return JsonResponse({'code':400,'errmsg':'用户名或密码不正确'})
        #　 user 不为Ｎｏｎｅ　说明登录成功继续执行后续代码

        # 5.状态保持
        from django.contrib.auth import login
        login(request,user)
        # 6.要根据是否记住登录(类似于 mail.163.com中的 10免登录 本质是设置session过期时间)
        if remembered:
            # remembered 用户 判断 是否勾选 记住登录状态
            # 如果勾选 ,则让 session有效期为 2周(14天)
            request.session.set_expiry(None)
        else:
            # 如果未勾选,则 让 session有效期为 浏览会话结束之后
            request.session.set_expiry(0)


        # 7.返回响应
        response = JsonResponse({'code':0,'errmsg':'ok'})
        #设置cookie,
        # 注意: key 必须是 username 因为前端写死了
        response.set_cookie('username',username,max_age=14*24*3600)

        return response


# 退出登录
class LogoutView(View):

    def delete(self,request):

        # 1. 删除状态保持信息
        # request.session.clear()
        # request.session.flush()

        # djago -- login
        # django 既然实现了 状态保持的方法
        # 也会实现 状态删除的方法
        from django.contrib.auth import logout
        logout(request)

        # 2. 把username 的cookie信息删除

        response = JsonResponse({'code':0,'errmsg':'ok'})

        response.delete_cookie('username')

        return response

#################################################
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate

"""
LoginRequiredMixin : 是判断用户是否登录


authenticate       : 是判断用户名和密码是否正确
"""

# 用户中心 应该是 必须用户登录才可以访问

# LoginRequiredMixin 做了什么???
#如果用户没有登录，则返回 没有权限操作
# 如果用户登录了，则 继续调用父类的dispatch方法


# class UserInfoView(View,LoginRequiredMixin):   # 1   View 就直接把dispatch 走完了 不会调用 LoginRequiredMixin的dispatch

from utils.views import LoginRequiredJSONMixin
"""
在退出登录的情况下 进行验证

LoginRequiredJSONMixin      它判断没有登录 返回JSON

LoginRequiredMixin          它判断没有登录 返回重定向

"""
# class UserInfoView(LoginRequiredMixin,View):   # 2  LoginRequiredMixin 返回重定向 accounts/login/
class UserInfoView(LoginRequiredJSONMixin,View):   # 2   LoginRequiredMixin 的dispath, 然后判断.   返回的就是JSON

    def get(self,request):
        """
        1. 判断 必须是登录用户
        2. 获取用户信息
        3. 返回响应
        :param request:
        :return:
        """
        # 用户的信息在哪里呢???
        #request.user
        # request里有一个 user属性
        # 这个user属性 其实是系统 根据我们的session信息 自动帮我们添加的  (为了我们操作方便)
        # 如果我们已经真的登录了 request.user 就是 我们数据库中的 那个 user实例对象
        user=request.user
        user_info = {
            'username':user.username,
            'mobile':user.mobile,
            'email':user.email,
            'email_active': user.email_active   # 明天才讲 email_active 先给一个固定值
        }
        # 注意: 用户信息的JSON数据 中  用户的信息对应的key 必须是 info_data 因为前端写死了
        return JsonResponse({'code':0,'errmsg':'ok','info_data':user_info})

##########################################################################
# 邮件保存
from utils.views import LoginRequiredJSONMixin
class EmailView(LoginRequiredJSONMixin,View):

    def put(self,request):
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
        # put 请求的数据 也在 body中
        data = json.loads(request.body.decode())
        # 3. 提取参数
        email = data.get('email')
        # 4. 验证参数(省略--作业)
        # 5. 更新用户信息(数据入库)
        user = request.user
        user.email=email
        user.save()
        # 6. 发送激活邮件
        #  想要实现发送邮件,我们需要先设置 邮件服务器

        # from django.core.mail import send_mail
        # #subject, message, from_email, recipient_list,
        #
        # #subject,   主题
        # subject='美多商城激活邮件'
        #
        # # message,  邮件内容
        # message = ''
        #
        # # from_email,   谁发的邮件
        # from_email = '美多商城<qi_rui_hua@163.com>'
        #
        # # recipient_list,  收件人列表 ['邮箱','邮箱',,]
        # recipient_list = [email]
        # # recipient_list = [email,'qi_rui_hua@126.com']
        #
        # # 支持 HTML
        # html_message = '<a href="#">点击激活</a>'
        #
        # send_mail(subject,
        #           message,
        #           from_email,
        #           recipient_list,
        #           html_message=html_message)

        # 生成一个 html_message

        # token 数据是一个加密的数据,这个数据中 包含用户信息就可以
        from apps.users.utils import generic_user_id

        token = generic_user_id(user.id)

        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s'%token

        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(email,html_message)

        # 7. 返回响应
        return JsonResponse({'code':0})


class VerifyEmailView(View):

    def put(self,request):
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
        data=request.GET
        # 2. 提取数据
        token=data.get('token')
        # 3. 对数据进行解密操作
        from apps.users.utils import check_user_id
        user_id=check_user_id(token)
        # 4. 判断有没有user_id
        if user_id is None:
            # 5. 如果没有则说明 token过期了
            return JsonResponse({'code':400,'errmsg':'链接时效'})
        # 6. 如果有,则查询用户信息
        # 为什么要查询??? 因为有可能用户换了一个浏览器来激活 这个时候 request.user 就不是登录用户了
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'链接时效'})
        # 7. 改变用户的邮箱激活状态
        user.email_active=True
        user.save()
        # 8. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})





################地址管理################################
from apps.users.models import Address

class CreateAddressView(LoginRequiredJSONMixin,View):

    def post(self,request):
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
        # 1. 必须是登录用户才可以新增地址   LoginRequiredJSONMixin
        # 2. 接收参数
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
            'id':address.id,
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

        return JsonResponse({'code':0,'errmsg':'ok','address':address_dict})



######地址查询#######################################

class AddressesListView(LoginRequiredJSONMixin,View):

    def get(self,request):
        """
        1. 必须是登录用户才可以获取地址
        2. 根据用户信息查询地址信息
        3. 需要对查询结果集进行遍历, 转换为字典列表
        4. 返回响应
        :param request:
        :return:
        """
        # 1. 必须是登录用户才可以获取地址  LoginRequiredJSONMixin
        # 2. 根据用户信息查询地址信息
        addresses=Address.objects.filter(user=request.user,  # user 条件必须有
                                         is_deleted=False)
        # 3. 需要对查询结果集进行遍历, 转换为字典列表
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id':address.id,
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
        """
        {
         'code': 0,
         'errmsg': 'ok',
         'addresses': [],
         'default_address_id': 1
        }
        """
        # User 表中有一个属性(字段) -- default_address_id
        return JsonResponse({'code':0,
                             'errmsg':'ok',
                             'addresses':addresses_list,
                             'default_address_id':request.user.default_address_id})


###############################################################
# 新增用户浏览记录
from apps.goods.models import SKU
from django_redis import get_redis_connection

class UserHistoryView(LoginRequiredJSONMixin,View):

    def post(self,request):
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
        # 1. 接收请求  JSON request.body
        data = json.loads(request.body.decode())
        # 2. 提取参数
        sku_id=data.get('sku_id')
        # 3. 验证参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        # 4. 连接redis
        redis_cli=get_redis_connection('history')
        # 5. 去重数据 (列表删除数据)  sku_id
        """
        LREM key count value

        根据参数 count 的值，移除列表中与参数 value 相等的元素。
        
        count 的值可以是以下几种：
        
        count > 0 : 从表头开始向表尾搜索，移除与 value 相等的元素，数量为 count 。
        count < 0 : 从表尾开始向表头搜索，移除与 value 相等的元素，数量为 count 的绝对值。
        count = 0 : 移除表中所有与 value 相等的值。
        """
        redis_cli.lrem(request.user.id,0,sku_id)
        # 6. 添加数据
        # lpush(key,value)
        redis_cli.lpush(request.user.id,sku_id)
        # 7. 最多保存5条记录
        """
        LTRIM key start stop

        对一个列表进行修剪(trim)，就是说，让列表只保留指定区间内的元素，不在指定区间之内的元素都将被删除。
        
        举个例子，执行命令 LTRIM list 0 2 ，表示只保留列表 list 的前三个元素，其余元素全部删除。
        """
        redis_cli.ltrim(request.user.id,0,4)
        # 8. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})


    def get(self,request):
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
        # 1. 必须是登录用户  LoginRequiredJSONMixin
        # 2. 获取用户信息
        user=request.user
        # 3. 连接redis
        redis_cli=get_redis_connection('history')

        # 4. 查询浏览记录 [1,2,3]
        # lrange(key, start,stop)
        sku_ids=redis_cli.lrange(user.id,0,-1)

        skus=[]

        # 5. 遍历列表数据,查询商品详细信息
        for id in sku_ids:
            # 商品id在新增历史记录的时候 验证过,异常捕获可加可不加(最好加)
            sku = SKU.objects.get(id=id)
            # 6. 将对象转换为字典数据
            skus.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url   # url 调用自定义存储类的url属性
            })
        # 7. 返回响应
        return JsonResponse({'code':0,'skus':skus,'errmsg':'ok'})


