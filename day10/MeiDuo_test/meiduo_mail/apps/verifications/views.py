from random import randint
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from celery_tasks.tasks.tasks import send_message
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render


# Create your views here.

class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 300, text)

        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):
        # 1. 接收参数
        # 2. 获取参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 3. 验证参数
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '缺少关键参数'})

        # 4. 提取 redis 中图片验证码
        redis_cli = get_redis_connection('code')
        redis_text = redis_cli.get(uuid)

        # 5. 把 redis 中的图片验证码删除
        redis_cli.delect(uuid)

        # 6. 用户的图片验证码和 redis 进行比对
        if image_code.lower() != redis_text.decode().lower():
            return JsonResponse({'code': 400, 'errmsg': '验证码错误'})

        # 7. 将短信验证码保存到redis中
        sms_num = randint(100000, 999999)

        pipeline = redis_cli.pipeline()
        pipeline.setex(mobile, 300, sms_num)
        pipeline.setex('send_flag_%s' % mobile, 60, 1)

        # 8. 通过程序生成短信验证码 - 发送短信
        send_message.delay(mobile, sms_num)
        # pipeline = redis_cli.pipeline()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
