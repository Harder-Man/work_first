from django.urls import path
from apps.verifications.views import ImageCodeView,SmsCodeView

urlpatterns = [
    # path('image_codes/<转换器的名字:变量参数>/',ImageCodeView.as_view()),
    path('image_codes/<uuid:uuid>/',ImageCodeView.as_view()),

    # 短信
    path('sms_codes/<mobile>/',SmsCodeView.as_view()),
]