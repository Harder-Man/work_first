from random import randint

from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from Celery_tasks.sms.tasks import send_message
from django.http.response import JsonResponse, HttpResponse


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_cli = get_redis_connection('code')
        redis_cli.setex(uuid, 300, text)
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request, mobile):

        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '验证码不能为空'})

        redis_cli = get_redis_connection('code')
        text = redis_cli.get(uuid)

        redis_cli.delete(uuid)

        if image_code.lower() != text.decode().lower():
            return JsonResponse({'code': 400, 'errmsg': '验证码错误'})

        num = randint(100000, 999999)

        pipeline = redis_cli.pipeline()

        pipeline.setex(mobile, 300, num)
        pipeline.setex('send_sms_%s' % mobile, 60, 1)

        pipeline.execute()

        send_message.delay(mobile, num)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
