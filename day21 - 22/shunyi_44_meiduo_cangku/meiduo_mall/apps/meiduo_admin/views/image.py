from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.image import SKUImageModelSerializer, SimpleSKUModelSerializer
from apps.meiduo_admin.utils import PageNUm


class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNUm

    def create(self, request, *args, **kwargs):
        upload_image = request.FILES.get('image')
        sku_id = request.data.get('data')

        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return Response({'msg': '没有此数据'})

        image_url = ''

        new_image = SKU.objects.create(
            sku_id=sku_id,
            image=image_url
        )

        return Response({'id': new_image.id,
                         'image': new_image.image.url,
                         'sku': sku_id},
                        status=201)


class SimpleSKUListAPIView(ListAPIView):
    queryset = SKU.objects.all()

    serializer_class = SimpleSKUModelSerializer
