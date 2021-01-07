from django.urls import path
from apps.oauth.views import *

urlpatterns = [
    path('',QQUserView.as_view()),

]