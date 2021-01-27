from django.urls import path
from apps.areas.views import ProvienceView,SubAreaView

urlpatterns = [
    # 获取省份信息
    path('areas/',ProvienceView.as_view()),

    # 市区县数据获取
    path('areas/<pk>/',SubAreaView.as_view()),
]