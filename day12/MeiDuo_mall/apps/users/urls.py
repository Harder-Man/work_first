from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('usernames/<uc:username>/count/', UsernameCountView.as_view()),

    # 用户注册
    path('register/', RegisterView.as_view()),

    # 用户登录
    path('login/', LoginView.as_view()),
]
