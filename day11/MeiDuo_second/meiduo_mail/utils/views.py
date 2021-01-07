from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class LoginRequireJsonMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '没有登录,请登录'})
