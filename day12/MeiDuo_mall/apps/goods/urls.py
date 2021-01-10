from django.urls import path
from apps.goods.views import *

urlpatterns = [
    path('index/', IndexView.as_view()),

    # 列表显示
    path('list/<category_id>/skus', ListView.as_view()),

    # 热销显示
    path('hot/<category_id>/', HotView.as_view()),

    # 详情页面
    path('detail/<sku_id>/', DetailView.as_view()),

    # 访问量
    path('detail/visit/<category_id>/', CategoryVisitView.as_view()),

    # 用户浏览记录
    path('browse_histories/', UserHistoryView.as_view()),
]
