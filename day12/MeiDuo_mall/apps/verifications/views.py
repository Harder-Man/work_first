from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http.response import JsonResponse,HttpResponse
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