from django.urls import path
from book.views import *

urlpatterns = [
    path('index/', Index.as_view()),
    path('login/', isLogin.as_view()),

]