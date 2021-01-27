from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.users.models import User


class UserActiveAPIView(APIView):

    def get(self, request):
        # 1. 获取今天的date
        today = date.today()

        # 2.过滤查询
        count = User.objects.filter(last_login__gte=today).count()

        return Response({'count': count})


class UserOrderAPIView(APIView):

    def get(self, request):
        today = date.today()

        count = User.objects.filter(orderinfo__create_time__gte=today).count()

        return Response({'count': count})


class MonthUserAPIView(APIView):

    def get(self, request):
        """
        1. 先获取今天的日期
        2. 获取30天前的日期
        3. 初始化字典列表
        4. 遍历每一天的新增用户量
        5. 将数据添加到字典
        6. 返回响应
        :param request:
        :return:
        """
        # 1. 先获取今天的日期
        today = date.today()

        # 2. 获取30天前的日期
        before_date = today - timedelta(days=30)

        # 3. 初始化字典列表
        data_list = []

        # 4. 遍历每一天的新增用户量
        for i in range(0, 30):
            begin_date = before_date + timedelta(days=i)
            end_date = before_date + timedelta(days=i + 1)
            count = User.objects.filter(date_joined__gte=begin_date,
                                        date_joined__lt=end_date).count()
            # 5. 将数据添加到字典
            data_list.append({
                'count': count,
                'date': begin_date
            })

        # 6. 返回响应
        return Response(data_list)


class UserIncrementAPIView(APIView):

    def get(self, request):
        today = date.today()
        count = User.objects.filter(date_joined__gte=today).count()

        return Response({
            'count': count,
            'date': today
        })


class UserTotalCountAPIView(APIView):

    def get(self, request):
        today = date.today()

        count = User.objects.count()

        return Response({
            'count': count,
            'date': today
        })
