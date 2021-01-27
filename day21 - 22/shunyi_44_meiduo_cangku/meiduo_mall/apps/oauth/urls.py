from django.urls import path
from apps.oauth.views import QQUserView

urlpatterns = [
    # 获取前端发送的 code 的url
    path('oauth_callback/',QQUserView.as_view()),
]