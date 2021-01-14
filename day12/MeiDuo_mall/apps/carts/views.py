import json

from django.shortcuts import render
from django.http.response import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from utils.views import LoginRequiredJsonMixin


class CartView(LoginRequiredJsonMixin, View):

    def post(self, request):
        """
        0. 获取用户信息
        1. 接收参数
        2. 提取参数
        3. 验证参数
        4. 数据入库
        4.1 连接redis
        4.2 操作hash
        4.3 操作set
        5. 返回响应
        :param request:
        :return:
        """
        # 0. 获取用户信息
        user = request.user

        # 1. 接收参数
        data = json.loads(request.body.decode())

        # 2. 提取参数
        sku_id = data.get('sku_id')
        count = data.get('count')

        # 3. 验证参数
        if not all([sku_id, count]):
            return JsonResponse({"code": 400, 'errmsg': '参数不全'})

        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        try:
            count = int(count)
        except:
            count = 1

        # 4. 数据入库
        # 4.1 连接redis
        redis_cli = get_redis_connection('carts')

        # 4.2 操作hash
        redis_cli.hset('carts_%s' % user.id, sku_id, count)

        # 4.3 操作set
        redis_cli.sadd('selected_%s' % user.id, sku_id)

        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def get(self, request):
        """
        0. 必须是登录用户,获取用户信息
        1. 连接redis
        2. 获取hash {sku_id:count,sku_id:count} key和value是 bytes
        3. 获取 set {sku_id,sku_id} 选中商品id value是 bytes
        4. 获取所有购物车中的商品id
        5. 遍历所有商品id 根据商品id查询商品信息
        6. 将对象转换为字典 (数量,选中状态和总价)
        7. 返回响应
        :param request:
        :return:
        """
        # 0. 必须是登录用户,获取用户信息
        user = request.user

        # 1. 连接redis
        redis_cli = get_redis_connection('carts')

        # 2. 获取hash {sku_id:count,sku_id:count} key和value是 bytes
        sku_id_count = redis_cli.hgetall('carts_%s' % user.id)

        # 3. 获取 set {sku_id,sku_id} 选中商品id value是 bytes
        selected_ids = redis_cli.smembers('selected_%s' % user.id)

        # 4. 获取所有购物车中的商品id
        ids = sku_id_count.keys()
        cart_sku = []
        # 5. 遍历所有商品id 根据商品id查询商品信息
        for id in ids:
            sku = SKU.objects.get(id=id)
            # 6. 将对象转换为字典 (数量,选中状态和总价)
            cart_sku.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
                'count': int(sku_id_count[id]),
                'selected': id in selected_ids,
                'amount': sku.price * int(sku_id_count[id])
            })

        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_sku})
