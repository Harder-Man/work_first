from django.urls import path
from apps.carts.views import *

urlpatterns = [
    path('carts/', CartView.as_view()),
]
