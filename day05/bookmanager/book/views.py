from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


# Create your views here.


class Index(View):

    def get(self, request):
        return HttpResponse("get")

    def post(self, request):
        return HttpResponse('post')


class isLogin(LoginRequiredMixin, View):

    def get(self, request):
        return HttpResponse('get')

    def post(self, request):
        return HttpResponse('post')
