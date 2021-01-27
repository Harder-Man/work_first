from django.urls import path
from apps.users.views import UsernameCountView,RegisterView,LoginView
from apps.users.views import LogoutView,UserInfoView,EmailView
from apps.users.views import VerifyEmailView,CreateAddressView
from apps.users.views import AddressesListView,UserHistoryView

urlpatterns = [
    # path('usernames/<username>/count/',UsernameCountView.as_view()),
    path('usernames/<uc:username>/count/',UsernameCountView.as_view()),

    #########注册url####################
    path('register/',RegisterView.as_view()),

    ###########登录####################
    path('login/',LoginView.as_view()),

    #########退出登录########
    path('logout/',LogoutView.as_view()),

    #########个人中心########
    path('info/',UserInfoView.as_view()),
    #########邮件保存########
    path('emails/',EmailView.as_view()),
    #########激活邮件########
    path('emails/verification/',VerifyEmailView.as_view()),

    #########地址管理########
    path('addresses/create/',CreateAddressView.as_view()),

    #########地址查询########
    path('addresses/',AddressesListView.as_view()),

    #########用户浏览记录########
    path('browse_histories/',UserHistoryView.as_view()),
]