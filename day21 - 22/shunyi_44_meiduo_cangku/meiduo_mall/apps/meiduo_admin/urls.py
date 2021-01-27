from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.meiduo_admin.login import admin_obtain_token
from apps.meiduo_admin.views import home, user, image

urlpatterns = [
    path('authorizations/', admin_obtain_token),

    # 日活用户
    path('statistical/day_active/', home.UserActiveAPIView.as_view()),

    # 日订单量
    path('statistical/day_orders/', home.UserOrderAPIView.as_view()),

    # 月增用户折线图
    path('statistical/month_increment/', home.MonthUserAPIView.as_view()),

    # 获取用户数据
    path('users/', user.UserListAPIView.as_view()),

    # 图片中 获取sku数据
    path('skus/simple/', image.SimpleSKUListAPIView.as_view()),
]

route = DefaultRouter()
route.register('skus/images', image.ImageModelViewSet, basename='image')
urlpatterns += route.urls
