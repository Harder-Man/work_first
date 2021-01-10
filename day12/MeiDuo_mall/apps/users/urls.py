from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('usernames/<uc:username>/count/', UsernameCountView.as_view()),
]
