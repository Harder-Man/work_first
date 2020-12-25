from django.urls import path
from book.views import *

urlpatterns = [
    # path('<book_id>/<name_id>/', index)
    path('get/', get_request),
    path('post/', post_request),
    path('json/', json_request),
]
