from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('usernames/<uc:username>/count/', UserNamesView.as_view()),
    # path('usernames/<uc:username>/count/', UserNamesView.as_view()),
    path('register/', JsonData.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', UserInfoView.as_view()),
    path('emails/', EmailView.as_view()),
]
