from django.urls import path
from apps.verifications.views import *


urlpatterns = [
    path('image_codes/<uuid:uuid>/', ImageCodeView.as_view()),
]