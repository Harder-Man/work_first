from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from utils.views import LoginRequiredJSONMixin
from apps.users.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU

# 提交订单页面展示
class OrderSubmitView(LoginRequiredJSONMixin,View):

    def get(self,request):
        """
        0. 获取用户信息
        1. 获取地址信息
            1.1 查询登录用户的地址信息
            1.2 将对象列表转换为字典列表
        2. 获取购物车中选中商品信息
            2.1 连接redis
            2.2 获取set
            2.3 获取hash
            2.4 遍历选中商品的id
            2.5 查询商品信息
            2.6 将对象转换为字典(记得添加购物车数量)
        3. 运费
        4. 组织数据返回响应
        :param request:
        :return:
        """
        # 0. 获取用户信息
        user=request.user

        # 1. 获取地址信息
        #     1.1 查询登录用户的地址信息
        addresses=Address.objects.filter(user=user,is_deleted=False)
        #     1.2 将对象列表转换为字典列表
        addresses_list=[]
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        # 2. 获取购物车中选中商品信息
        #     2.1 连接redis
        redis_cli=get_redis_connection('carts')
        #     2.2 获取set  选中商品的id
        selected_ids=redis_cli.smembers('selected_%s'%user.id)
        # {b'1',b'2',...}
        #     2.3 获取hash    所有商品的id 和数量
        sku_id_counts=redis_cli.hgetall('carts_%s'%user.id)
        # {b'1':b'5',b'2':b'3'}
        #     2.4 遍历选中商品的id
        selected_carts=[]
        for id in selected_ids:
            #     2.5 查询商品信息
            sku = SKU.objects.get(id=id)
            #     2.6 将对象转换为字典(记得添加购物车数量)
            selected_carts.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(sku_id_counts[id]),                    # 选中的数量 记得转换类型
                'price':sku.price
                # 'amount': sku.price*int(sku_id_counts[id])          # 一个商品的小计  单价*数量
            })
        # 3. 运费
        freight = 10
        # 4. 组织数据返回响应
        context = {
            'addresses':addresses_list,
            'skus':selected_carts,
            'freight':freight
        }

        return JsonResponse({'code':0,'errmsg':'ok','context':context})
import json
from apps.orders.models import OrderInfo,OrderGoods
class OrderCommitView(LoginRequiredJSONMixin,View):

    def post(self,request):
        """
        0.判断必须是登录用户,获取用户信息  user
        1. 接收参数   address_id,pay_method
        2. 提取参数
        3. 验证参数
        4. 数据入库
            4.1 先保存订单基本信息
                ① 生成订单id order_id
                ② 根据支付方式,设置订单状态
                ③ 运费  10
                ④ 订单总数量 =0  和 订单总金额 = 0 (我们需要遍历选中商品的id,查询商品详细信息,计算总金额)

            4.2 保存订单商品信息
                ① 连接redis
                ② 获取选中商品的id {sku_id,sku_id}
                ③ 获取hash数据(数量)   {sku_id:count,sku_id:count}
                ④ 遍历选中商品的id
                ⑤ 查询商品详细信息
                ⑥ 获取库存, 判断用户购买的数量是是否满足库存剩余
                ⑦ 如果不满足,则下单失败
                ⑧ 如果满足, SKU的销量增加,SKU的库存减少
                ⑨ 保存订单商品信息
                ⑩ 统计订单总数量和订单总金额
            4.3 统计完成之后,再更新订单基本信息数据
            4.4 清除 redis中选中商品的信息
         5. 返回响应
        :param request:
        :return:
        """
        # 0.判断必须是登录用户,获取用户信息  user
        user=request.user
        # 1. 接收参数   address_id,pay_method
        data=json.loads(request.body.decode())
        # 2. 提取参数
        address_id=data.get('address_id')
        pay_method=data.get('pay_method')
        # 3. 验证参数
        try:
            address=Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此地址'})

        # if pay_method not in [1,2]:   [1,2] 是没问题的, 可读性不高
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code':400,'errmsg':'支付方式不正确'})
        # 4. 数据入库
        #     4.1 先保存订单基本信息
        #         ① 生成订单id order_id
        # order_id = '202111294501' + 9位的用户id   1,2
        from datetime import datetime
        from django.utils import timezone
        # timezone.localtime().strftime() 获取本地时间(我们没有设置,获取的就是格林尼治时间) 将时间转换为字符串
        # Y     Year
        # m     month
        # d     day
        # H     Hour
        # M     Minute
        # S     Second
        # 注意 大小写

        # '%09d' 不满9位 用0补齐
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d'%user.id
        #         ② 根据支付方式,设置订单状态
        #  现金支付的状态是 待发货   支付宝支付的状态是 待支付
        # if pay_method == 1:  #现金
        #     status = 2
        # else:
        #     # 支付宝
        #     status = 1
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:  # 现金
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            # 支付宝
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        #         ③ 运费  10
        # 金钱我们都使用 Decimal 类型 这个就是货币类型
        # 货币类型能够保证我们金额的正确性
        from decimal import Decimal
        # Decimal(字符串)  字符串得是数值
        freight = Decimal('10')
        #         ④ 订单总数量 =0  和 订单总金额 = 0 (我们需要遍历选中商品的id,查询商品详细信息,计算总金额)
        total_count=0
        total_amount=Decimal('0')

        from django.db import transaction
        # with 语句 部分代码使用事务
        with transaction.atomic():

            # 一.开始点
            start_point=transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            #     4.2 保存订单商品信息
            #         ① 连接redis
            redis_cli=get_redis_connection('carts')
            #         ② 获取选中商品的id {sku_id,sku_id}
            selected_ids=redis_cli.smembers('selected_%s'%user.id)
            #         ③ 获取hash数据(数量)   {sku_id:count,sku_id:count}
            sku_id_counts=redis_cli.hgetall('carts_%s'%user.id)
            #         ④ 遍历选中商品的id
            for id in selected_ids:
                while (True):
                    #         ⑤ 查询商品详细信息
                    sku=SKU.objects.get(id=id)
                    #         ⑥ 获取库存, 判断用户购买的数量是是否满足库存剩余
                    mysql_stock=sku.stock
                    custom_count=int(sku_id_counts[id])
                    #         ⑦ 如果不满足,则下单失败
                    if custom_count > mysql_stock:

                        # 二. 回滚点   回滚到哪里去
                        transaction.savepoint_rollback(start_point)

                        return JsonResponse({'code':400,'errmsg':'下单失败,库存不足'})
                    #         ⑧ 如果满足, SKU的销量增加,SKU的库存减少

                    # 模拟并发的情况
                    import time
                    time.sleep(7)
                    # 进程睡 7秒

                    # sku.sales += custom_count           #销量增加
                    # sku.stock -= custom_count           #库存减少
                    # sku.save()  # 记得保存

                    # 1.记录之前的值
                    # 可以用库存,也可以用销量    15
                    old_stock=sku.stock

                    # 2. 更新前，判断记录的值 是否和现在查询的值一致
                    new_stock=sku.stock-custom_count
                    new_sales=sku.sales+custom_count

                    result = SKU.objects.filter(id=id,stock=old_stock).update(sales=new_sales,stock=new_stock)
                    # result =0 表示更新数据失败
                    # result =1 表示更新数据成功
                    if result == 0:
                        continue
                        # transaction.savepoint_rollback(start_point)
                        # return JsonResponse({'code':400,'errmsg':'下单失败'})

                    #         ⑨ 保存订单商品信息
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=custom_count,
                        price=sku.price
                    )
                    #         ⑩ 统计订单总数量和订单总金额
                    order.total_count += custom_count       #累加总数量
                    order.total_amount += (custom_count*sku.price)  #累加总金额
                    break
            #     4.3 统计完成之后,再更新订单基本信息数据
            # for 结束 统一保存(更新)订单总数量和总金额(入库)
            order.save()

            # 三 提交
            transaction.savepoint_commit(start_point)

        #     4.4 清除 redis中选中商品的信息 (下午再写)
        #  5. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok','order_id':order_id})