from rest_framework.generics import ListCreateAPIView
from apps.meiduo_admin.utils import PageNUm
from apps.users.models import User
from apps.meiduo_admin.serializers.user import UserModelSerializer


class UserListAPIView(ListCreateAPIView):

    # queryset = User.objects.all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return User.objects.filter(username__contains=keyword)
        else:
            return User.objects.all()

    serializer_class = UserModelSerializer

    pagination_class = PageNUm
