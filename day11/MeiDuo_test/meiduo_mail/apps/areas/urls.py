from django.urls import path
from apps.areas.views import *

urlpatterns = [
    path('areas/', ProvinceView.as_view()),
]