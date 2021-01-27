from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def jwt_response_payload_handler(token, user=None, request=None):
    # token             系统生成的token
    # user=None         登录认证的user
    # request=None      请求
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }


class PageNUm(PageNumberPagination):
    page_size = 2

    # 设置前段的请求参数: pagesize
    page_size_query_param = 'pagesize'

    def get_paginated_response(self, data):

        return Response({
            'count': self.page.paginator.count,
            'lists':data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.page_size,
        })
