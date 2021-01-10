from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('usernames/<uc:username>/count/', UsernameCountView.as_view()),

    # 用户注册
    path('register/', RegisterView.as_view()),

    # 用户登录
    path('login/', LoginView.as_view()),

    # 用户退出
    path('logout/', LogoutView.as_view()),

    # 用户中心
    path('info/', UserInfoView.as_view()),

    # 邮箱保存
    path('emails/', EmailView.as_view()),

    # 激活邮件
    path('emails/verification/', VerifyEmailView.as_view()),

    # 地址管理
    path('addresses/', AddressListView.as_view()),
]
