from django.urls import path
from apps.oauth.views import *

urlpatterns = [
    path('oauth_callback/', QQUserView.as_view()),
]