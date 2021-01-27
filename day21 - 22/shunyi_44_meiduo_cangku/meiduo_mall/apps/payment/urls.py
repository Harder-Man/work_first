from django.urls import path
from apps.payment.views import PayURLView,PayCommitView

urlpatterns = [

    # 支付完成
    path('payment/status/',PayCommitView.as_view()),

    #
    path('payment/<order_id>/',PayURLView.as_view()),




]