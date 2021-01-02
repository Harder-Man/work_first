from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('usernames/<uc:username>/count/', UserNamesView.as_view()),
    # path('usernames/<uc:username>/count/', UserNamesView.as_view()),
    path('register/', JsonData.as_view()),
]
