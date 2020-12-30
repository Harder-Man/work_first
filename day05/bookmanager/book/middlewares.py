from django.utils.deprecation import MiddlewareMixin


class BookMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        print('请求前1')

    def process_response(self, request, response):
        print('响应前111')
        return response


class BookMiddleWare2(MiddlewareMixin):

    def process_request(self, request):
        print('请求前22')

    def process_response(self, request, response):
        print('响应前222')
        return response
