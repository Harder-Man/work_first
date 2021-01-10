from django.urls import path
from apps.areas.views import *

urlpatterns = [
    # 省
    path('areas/', ProvinceView.as_view()),

    # 市区
    path('areas/<pk>/', SubAreaView.as_view()),
]
