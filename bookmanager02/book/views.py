from django.shortcuts import render
from django.http.response import HttpResponse
import json

'''
# Create your views here.
def index(request, book_id, name_id):
    print(book_id, name_id)

    return HttpResponse('今天的你努力了么！')
'''


def get_request(request):
    recv = request.GET
    # a = recv['a']
    a = recv.get('a')
    b = recv.getlist('b')
    print(a, b)

    return HttpResponse('今天的你努力了么!')


def post_request(request):
    recv = request.POST
    # for i in recv:
    #     print(i, recv[i])
    for i, j in recv.items():
        print(i, j)

    print(recv)

    return HttpResponse('今天的你努力了么!')


def json_request(request):
    recv = request.body
    print(recv)

    recv_json_str = recv.decode()
    print(recv_json_str)

    recv_dict = json.loads(recv_json_str)
    print(recv_dict)

    return HttpResponse('今天的你努力了么!')
