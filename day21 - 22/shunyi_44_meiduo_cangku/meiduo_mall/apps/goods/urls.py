from django.urls import path
from apps.goods.views import IndexView,ListView,HotView,DetailView,CategoryVisitView
from apps.goods.views import MeiduoSearchView

urlpatterns = [

    path('index/',IndexView.as_view()),

    # 列表页面
    path('list/<category_id>/skus/',ListView.as_view()),

    # 热销
    path('hot/<category_id>/',HotView.as_view()),

    # 详情
    path('detail/<sku_id>/',DetailView.as_view()),

    # 访问量
    path('detail/visit/<category_id>/',CategoryVisitView.as_view()),

    # 搜索的url
    path('search/',MeiduoSearchView())
]