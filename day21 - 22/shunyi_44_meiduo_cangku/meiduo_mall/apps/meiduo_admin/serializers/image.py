from rest_framework.serializers import ModelSerializer
from apps.goods.models import SKUImage, SKU


class SKUImageModelSerializer(ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'



class SimpleSKUModelSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name']