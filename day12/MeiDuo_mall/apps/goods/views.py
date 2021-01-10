from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from utils.goods import *

# 导入商品模块
from apps.goods.models import *

# 导入分类也
from django.core.paginator import Paginator

# 获取面包屑数据
from utils.goods import get_breadcrumb


class IndexView(View):
    def get(self, request):
        """
        1. 获取分类数据
        2. 获取首页数据
        3. 组织数据 进行渲染
        :param request:
        :return:
        """
        # 1. 获取分类数据
        categories = get_categories()

        # 2. 获取首页数据
        contents = get_contents()

        # 3. 组织数据 进行渲染
        # 注意: key必须是这2个 因为模板中已经写死
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request, 'index.html', context)


class ListView(View):
    def get(self, request, category_id):
        """
        1. 接收参数
        2. 提取参数
        3. 根据分类id查询分类数据
        4. 验证参数(省略)
        4.1 page 整数
        4.2 page_size 整数
        4.3 ordering 只能是 create_time,price,sales
        5. 查询数据
        6. 分页数据
        7. 将对象列表转换为字典列表
        8. 返回响应
        :param request:
        :param category_id:
        :return:
        """
        # 1. 接收参数
        # 2. 提取参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')

        # 3. 根据分类id查询分类数据
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except:
            return JsonResponse({"code": 400, 'errmsg': '没有此分类'})

        # 4. 验证参数(省略)
        # 4.1 page 整数
        # 4.2 page_size 整数
        # 4.3 ordering 只能是 create_time,price,sales
        # 5. 查询数据
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)

        # 6. 分页数据
        paginator = Paginator(skus, per_page=page_size)
        page_skus = paginator.page(page)
        # 获取分了多少页
        total_num = paginator.num_pages

        sku_list = []
        # 7. 将对象列表转换为字典列表
        for item in page_skus:
            sku_list.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'default_image_url': item.default_image.url
            })

        # 获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 8. 返回响应
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'list': sku_list,
                             'count': total_num,
                             'breadcrumb': breadcrumb})


class HotView(View):

    def get(self, request, category_id):
        """
        1. 接收参数
        2. 根据分类id查询分类数据
        3. 查询SKU数据 条件就是 分类
        排序(根据销量 倒叙) 获取2条数据
        4. 将对象列表转换为字典列表
        5. 返回响应
        :param request:
        :param category_id:
        :return:
        """
        # 1. 接收参数
        # 2. 根据分类id查询分类数据
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '没有此分类'})

        # 3. 查询SKU数据 条件就是 分类
        skus = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[0:2]

        # 排序(根据销量 倒叙) 获取2条数据

        sku_list = []
        # 4. 将对象列表转换为字典列表
        for item in skus:
            sku_list.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'default_image_url': item.default_image.url
            })

        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': sku_list})


class DetailView(View):

    def get(self, request, sku_id):
        """
        1. 获取商品id
        2. 根据商品id查询商品信息
        3. 获取分类数据
        4. 获取面包屑数据
        5. 获取规格和规格选项数据
        6. 组织数据,进行HTML模板渲染
        7. 返回响应
        :param request:
        :param sku_id:
        :return:
        """
        # 1. 获取商品id
        # 2. 根据商品id查询商品信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})

        # 3. 获取分类数据
        categories = get_categories()

        # 4. 获取面包屑数据
        # sku 有 三级分类属性
        breadcrumb = get_breadcrumb(sku.category)

        # 5. 获取规格和规格选项数据
        # 传递 sku对象
        specs = get_goods_specs(sku)

        # 6. 组织数据,进行HTML模板渲染
        # context 的key 必须按照课件来!!!
        # 因为模板已经写死了
        context = {
            'sku': sku,
            'categories': categories,
            'breadcrumb': breadcrumb,
            'specs': specs
        }

        # 7. 返回响应
        return render(request, 'detail.html', context)
