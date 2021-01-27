from django.urls import path
from apps.orders.views import OrderSubmitView,OrderCommitView

urlpatterns = [
    path('orders/settlement/',OrderSubmitView.as_view()),

    # 提交订单
    path('orders/commit/',OrderCommitView.as_view()),
]