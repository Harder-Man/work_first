import re

from django.shortcuts import render
from random import randint
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http.response import JsonResponse,HttpResponse,HttpResponseBadRequest
from celery_tasks.sms_tasks.tasks import celery_send_message


# Create your views here.


class ImageCodeView(View):

    def get(self, request, uuid):
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
        # 4.生成图片验证码图片和获取图片验证码的内容
        text, image = captcha.generate_captcha()

        redis_cli = get_redis_connection('code')
        # 5.保存图片验证码
        redis_cli.setex(uuid, 300, text)

        # 6.返回图片响应
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        """
        1.接收参数
        2.获取参数
        3.验证参数(作业课下补齐)
        4.提取redis中的图片验证码
        5.把redis中的图片验证码删除
        6.用户的图片验证码和redis进行比对
        (redis的数据是bytes类型的,内容大小写统一)
        7. 通过程序生成短信验证码
        8. 将短信验证码保存到redis中
        9. 通过荣联云 发送短信
        10. 返回响应
        :param request:
        :param mobile:
        :return:
        """
        # 1.接收参数
        # 2.获取参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 3.验证参数(作业课下补齐)
        if not all([image_code, uuid]):
            return JsonResponse({'code':400, 'errmsg': '参数不全'})

        # 4.提取redis中的图片验证码
        redis_cli = get_redis_connection('code')
        redis_text = redis_cli.get(uuid)

        # 5.把redis中的图片验证码删除
        redis_cli.delete(uuid)

        # 6.用户的图片验证码和redis进行比对
        if image_code.lower() != redis_text.decode().lower():
            return JsonResponse({'code':400, 'errmsg': '验证码错误'})

        # 在生成短信验证码前 判断标记
        send_flag = redis_cli.get('send_flag_%s' % mobile)
        # send_flag 只要有值 就说明 在频繁操作
        if send_flag is not None:
            return HttpResponseBadRequest('不要频繁操作')
        # return JsonResponse({'code':400,'errmsg':'不要频繁操作'})


        # (redis的数据是bytes类型的,内容大小写统一)
        # 7. 通过程序生成短信验证码
        data = randint(100000, 999999)

        # 8. 将短信验证码保存到redis中
        pipeline = redis_cli.pipeline()
        pipeline.setex(mobile, 300, data)
        pipeline.setex('send_flag_%s' % mobile, 60, 1)
        pipeline.execute()

        # 9. 通过荣联云 发送短信
        celery_send_message.delay(mobile, data)

        # 10. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
