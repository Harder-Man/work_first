from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse

class ImageCodeView(View):

    def get(self,request,uuid):
        """
        1.接收请求
        2.提取参数
        3.验证参数
        4.生成图片验证码图片和获取图片验证码的内容
        5.保存图片验证码
        6.返回图片响应
        :param request:
        :param uuid:
        :return:
        """
        # 1.接收请求
        # 2.提取参数
        # 3.验证参数
        # xxxxx-xxxx-xxxx-xxxx-xxx
        # 为了回顾 昨天的 自定义转换器 所以我们这里还是用自定义转换器
        # if not re.match()

        # 4.生成图片验证码图片和获取图片验证码的内容
        from libs.captcha.captcha import captcha
        # captcha.generate_captcha()
        # 返回 第一个数据是 图片验证码的内容
        # 返回 第二个数据是 图片验证码的图片二进制
        text,image=captcha.generate_captcha()
        # 5.保存图片验证码 (redis)
        # 5.1 先连接redis
        from django_redis import get_redis_connection
        # get_redis_connection(配置中CACHES的名字)
        # 获取 redis 连接
        redis_cli=get_redis_connection('code')
        # 5.2 设置数据
        # setex key seconds value
        redis_cli.setex(uuid,300,text)

        # 6.返回图片响应
        # 注意事项!!!! 我们返回的不是JSON 而且 图片二进制
        # content_type='image/jpeg'
        # 告诉浏览器 哥们 我给你的二进制是图片哦 你要用图片的方式打开!!!
        return HttpResponse(image,content_type='image/jpeg')


#######短信验证码类视图############################
from django.http import JsonResponse,HttpResponseBadRequest

class SmsCodeView(View):

    def get(self,request,mobile):

        """
        1.接收参数
        2.获取参数
        3.验证参数(作业课下补齐)
        4.提取redis中的图片验证码
        5.把redis中的图片验证码删除
        6.用户的图片验证码和reids进行比对
            (redis的数据是bytes类型的,内容大小写统一)
        7. 通过程序生成短信验证码
        8. 将短信验证码保存到redis中
        9. 通过荣联云 发送短信
        10. 返回响应
        :param request:
        :param mobile:
        :return:
        """
        # 1.接收参数 (手机号,用户的图片验证码,uuid)
        # 2.获取参数
        # /sms_codes/<mobile>/?image_code=xxxx&image_code_id=xxxx

        # request.GET           1   查询字符串
        # request.POST          2   (form表单数据)
        # request.body          3  (JSON)
        # request.META          4 (请求头)
        # 用户的图片验证码
        image_code=request.GET.get('image_code')
        uuid=request.GET.get('image_code_id')
        # 3.验证参数(作业课下补齐)
        # 3.1 这2个变量 都要有数据
        # 3.2 image_code 的长度
        # 3.3 uuid

        # 4.提取redis中的图片验证码
        from django_redis import get_redis_connection
        redis_cli=get_redis_connection('code')

        redis_text=redis_cli.get(uuid)

        # 5.把redis中的图片验证码删除
        redis_cli.delete(uuid)

        # 6.用户的图片验证码和reids进行比对
        #     (redis的数据是bytes类型的,内容大小写统一)

        # 用户输入的  和 redis中的 不相等 就用户输错了
        # redis_text.decode() 将bytes类型 转换为 str
        # 内容大小写统一
        if image_code.lower() !=  redis_text.decode().lower():
            return JsonResponse({'code':400,'errmsg':'图片验证码错误'})

        # 在生成短信验证码前 判断标记
        send_flag = redis_cli.get('send_flag_%s'%mobile)

        # send_flag 只要有值 就说明 在频繁操作
        if send_flag is not None:
            return HttpResponseBadRequest('不要频繁操作')
            # return JsonResponse({'code':400,'errmsg':'不要频繁操作'})

        # 7. 通过程序生成短信验证码
        from random import randint
        sms_code=randint(100000,999999)
        # 8. 将短信验证码保存到redis中
        # setex key seconds value
        # 10分钟过期  600s
        # redis_cli.setex(mobile,600,sms_code)
        #添加一个标记
        # 标记就是 一个 1
        # 测试的时候 改长一点
        # redis_cli.setex('send_flag_%s'%mobile,300,1)

        # 8. 将短信验证码保存到redis中

        # ① 创建管道
        # 通过 redis 的客户端 创建一个 管道 pipeline()
        pipeline=redis_cli.pipeline()
        # ② 让管道收集指令
        pipeline.setex(mobile, 600, sms_code)
        pipeline.setex('send_flag_%s' % mobile, 300, 1)
        # ③ 执行管道  -- 一定要记得执行
        pipeline.execute()



        # 9. 通过荣联云 发送短信
        # from ronglian_sms_sdk import SmsSDK
        # accId = '8aaf07086246778ab6fe06b0'
        # accToken = '3b9e8ef5ec5848b483fe3f0ef0c'
        # appId = '8aaf0708624670f20162578206b6'
        #
        # # 9.1. 创建荣联云 实例对象
        # sdk = SmsSDK(accId, accToken, appId)
        # tid = '1'  # 我们发送短信的模板,值 只能是 1 因为我们是测试用户
        # mobile = '%s'%mobile  # '手机号1,手机号2'    给哪些手机号发送验证码,只能是测试手机号
        # datas = (sms_code, 10)  # ('变量1', '变量2')  涉及到模板的变量
        # # 您的验证码为{1},请于{2} 分钟内输入
        # # 您的验证码为666999,请于5 分钟内输入
        # # 9.2. 发送短信
        # sdk.sendMessage(tid, mobile, datas)

        from celery_tasks.sms.tasks import celery_send_sms_code
        #注意: 任务(函数)必须要调用 delay方法
        # delay的参数  同 任务(函数)的参数
        celery_send_sms_code.delay(mobile,sms_code)

        # 10. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})
