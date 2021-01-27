import json
from django.http import JsonResponse
from django_redis import get_redis_connection
from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin
from django.views import View
class CartsView(LoginRequiredJSONMixin,View):

    def post(self,request):
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
        user=request.user
        # 1. 接收参数
        data=json.loads(request.body.decode())
        # 2. 提取参数
        sku_id=data.get('sku_id')
        count=data.get('count')
        # 3. 验证参数
        if not all([sku_id,count]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})

        try:
            count=int(count)
        except Exception:
            count=1

        # 4. 数据入库
        #     4.1 连接redis
        redis_cli=get_redis_connection('carts')
        #     4.2 操作hash
        # HSET key field value
        redis_cli.hset('carts_%s'%user.id,sku_id,count)
        #     4.3 操作set
        # 默认就是选中 (淘宝是默认不选中) 结合具体需求
        #SADD key member [member ...]
        redis_cli.sadd('selected_%s'%user.id,sku_id)
        # 5. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})


    def get(self,request):
        """
        0. 必须是登录用户,获取用户信息
        1. 连接redis
        2. 获取hash  {sku_id:count,sku_id:count}   key和value是 bytes
        3. 获取 set  {sku_id,sku_id}      选中商品id   value是 bytes
        4. 获取所有购物车中的商品id
        5. 遍历所有商品id 根据商品id查询商品信息
        6. 将对象转换为字典 (数量,选中状态和总价)
        7. 返回响应
        :param request:
        :return:
        """
        # 0. 必须是登录用户,获取用户信息
        user=request.user
        # 1. 连接redis
        redis_cli=get_redis_connection('carts')
        # 2. 获取hash  {sku_id:count,sku_id:count}   key和value是 bytes
        # 获取所有的 hash key 对应的数据是
        """
        HGETALL key

        返回哈希表 key 中，所有的域和值。
        """
        sku_id_counts = redis_cli.hgetall('carts_%s'%user.id)
        # {sku_id:count,sku_id:count}

        # 3. 获取 set  {sku_id,sku_id}      选中商品id   value是 bytes
        """
        SMEMBERS key

        返回集合 key 中的所有成员。
        
        不存在的 key 被视为空集合。
        """
        selected_ids=redis_cli.smembers('selected_%s'%user.id)
        # {sku_id,sku_id}

        # 4. 获取所有购物车中的商品id
        # 字典.keys() 获取字典的所有的key
        ids = sku_id_counts.keys()
        # [1,2,3]

        carts_sku = []

        # 5. 遍历所有商品id
        for id in ids:

            #根据商品id查询商品信息
            sku=SKU.objects.get(id=id)

            # 6. 将对象转换为字典 (数量,选中状态和总价)
            carts_sku.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url,
                'count':int(sku_id_counts[id]),                         # 购物车数量   记得类型转换
                'selected': id in selected_ids,                         # 选中状态   通过程序判断
                'amount': sku.price*int(sku_id_counts[id])             # 当前购物车中 数量*单价的 总价
            })

        # 7. 返回响应
        return JsonResponse({'code':0,'cart_skus':carts_sku,'errmsg':'ok'})


    def put(self,request):
        """
        0. 获取用户信息
        1. 接收数据
        2. 提取数据
        3. 验证数据
        4. 更新数据
            4.1 连接redis
            4.2 更新hash
            4.3 更新set
        5. 返回响应
        :param request:
        :return:
        """
        # 0. 获取用户信息
        user=request.user
        # 1. 接收数据
        data=json.loads(request.body.decode())
        # 2. 提取数据
        sku_id=data.get('sku_id')
        count=data.get('count')
        selected=data.get('selected')
        # 3. 验证数据
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        # 4. 更新数据
        #     4.1 连接redis
        redis_cli=get_redis_connection('carts')
        #     4.2 更新hash
        # dict 直接 更新value值
        # 直接更新数据
        redis_cli.hset('carts_%s'%user.id,sku_id,count)

        #     4.3 更新set
        if selected:
            # 选中
            #添加到　集合中
            redis_cli.sadd('selected_%s'%user.id,sku_id)
        else:
            # 未选中
            # 应该从集合中 移除
            """
            SREM key member [member ...]

            移除集合 key 中的一个或多个 member 元素，不存在的 member 元素会被忽略。
            """
            redis_cli.srem('selected_%s'%user.id,sku_id)
        # 5. 返回响应  为了确保 前后端数据一致,我们要把后端的数据,再告诉前端
        cart_sku = {
            'id':sku_id,
            'name':sku.name,
            'count':count,
            'selected':selected,
            'price':sku.price,
            'amount':sku.price*int(count),
            'default_image_url':sku.default_image.url
        }
        return JsonResponse({'code':0,'cart_sku':cart_sku,'errmsg':'ok'})


    def delete(self,request):
        """
        1. 获取用户信息
        2. 接收参数
        3. 提取参数
        4. 验证参数
        5. 删除数据
            5.1 连接redis
            5.2 hash
            5.3 set
        6. 返回响应
        :param request:
        :return:
        """
        # 1. 获取用户信息
        user=request.user
        # 2. 接收参数
        data=json.loads(request.body.decode())
        # 3. 提取参数
        sku_id=data.get('sku_id')
        # 4. 验证参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        # 5. 删除数据
        #     5.1 连接redis
        redis_cli=get_redis_connection('carts')
        #     5.2 hash
        """
        HDEL key field [field ...]

        删除哈希表 key 中的一个或多个指定域，不存在的域将被忽略。
        """
        redis_cli.hdel('carts_%s'%user.id,sku_id)
        #     5.3 set
        """
        SREM key member [member ...]

        移除集合 key 中的一个或多个 member 元素，不存在的 member 元素会被忽略。
        """
        redis_cli.srem('selected_%s'%user.id,sku_id)
        # 6. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})
