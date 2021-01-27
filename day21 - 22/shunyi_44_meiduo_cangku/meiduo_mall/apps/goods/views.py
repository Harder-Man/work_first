from django.shortcuts import render

# Create your views here.
from django.views import View
from utils.goods import get_categories,get_contents

class IndexView(View):

    def get(self,request):

        """
        1. 获取分类数据
        2. 获取首页数据
        3. 组织数据 进行渲染
        :param request:
        :return:
        """
        # 1. 获取分类数据
        categories=get_categories()
        # 2. 获取首页数据
        contents=get_contents()
        # 3. 组织数据 进行渲染
        # 注意: key必须是这2个 因为模板中已经写死
        context = {
            'categories':categories,
            'contents':contents
        }
        return render(request,'index.html',context)


#######列表页面##########################################################################
from django.http import JsonResponse
class ListView(View):
    # http://www.meiduo.site:8000/list/115/skus/?page=1&page_size=5&ordering=-create_time
    def get(self,request,category_id):
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
        #list/115/skus/?page=1&page_size=5&ordering=-create_time
        # 1. 接收参数
        data=request.GET
        # 2. 提取参数
        page=data.get('page')               # 第几页
        page_size=data.get('page_size')     # 每页多少条数据
        ordering=data.get('ordering')       # 排序字段
        # 3. 根据分类id查询分类数据
        from apps.goods.models import GoodsCategory
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类'})
        # 4. 验证参数(省略)
        #     4.1 page 整数
        #     4.2 page_size 整数
        #     4.3 ordering 只能是 create_time,price,sales

        # 5. 查询数据
        # 查询的是具体某一个商品 SKU
        from apps.goods.models import SKU
        # 查询并且排序
        skus=SKU.objects.filter(category=category,is_launched=True).order_by(ordering)

        # 6. 分页数据
        # 导入分页类
        from django.core.paginator import Paginator
        # 创建分页实例
        # object_list,  列表数据
        # per_page      每页多少条数据

        paginator=Paginator(skus,per_page=page_size)
        # 获取指定页码的数据
        # page() 获取分页数据
        # page 查询参数
        page_skus=paginator.page(page)
        # 获取分了多少页
        total_num = paginator.num_pages


        # 7. 将对象列表转换为字典列表
        sku_list = []

        for item in page_skus:
            sku_list.append({
                'id':item.id,
                'name':item.name,
                'price':item.price,
                'default_image_url': item.default_image.url
            })

        # 获取面包屑数据
        from utils.goods import get_breadcrumb
        breadcrumb = get_breadcrumb(category)

        # 8. 返回响应
        return JsonResponse({'code':0,
                             'errmsg':'ok',
                             'list':sku_list,
                             'count':total_num,
                             'breadcrumb':breadcrumb})

from apps.goods.models import GoodsCategory,SKU
class HotView(View):

    def get(self,request,category_id):
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
        # 1. 接收参数 category_id
        # 2. 根据分类id查询分类数据
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类'})
        # 3. 查询SKU数据 条件就是 分类
        #     排序(根据销量 倒叙) 获取2条数据
        skus=SKU.objects.filter(category=category,is_launched=True).order_by('-sales')[0:2]
        # 4. 将对象列表转换为字典列表
        sku_list=[]
        for item in skus:
            sku_list.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'default_image_url': item.default_image.url
            })
        # 5. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok','hot_skus':sku_list})


###############################################
from utils.goods import get_breadcrumb,get_categories,get_goods_specs

class DetailView(View):


    def get(self,request,sku_id):
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
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此商品'})
        # 3. 获取分类数据
        categories = get_categories()
        # 4. 获取面包屑数据
        # sku 有 三级分类属性
        breadcrumb=get_breadcrumb(sku.category)
        # 5. 获取规格和规格选项数据
        # 传递 sku对象
        specs = get_goods_specs(sku)
        # 6. 组织数据,进行HTML模板渲染
        # context 的key 必须按照课件来!!!
        # 因为模板已经写死了
        context = {
            'sku':sku,
            'categories':categories,
            'breadcrumb':breadcrumb,
            'specs':specs
        }
        # 7. 返回响应
        return render(request,'detail.html',context)


###############商品分类访问量#######################################
from apps.goods.models import GoodsVisitCount
class CategoryVisitView(View):

    def post(self,request,category_id):
        """
        1. 获取分类id
        2. 根据分类id查询分类数据
        3. 获取当天日期
        4. 我们要查询数据库,是否存在 分类和日期 的记录
        5. 如果不存在 则新增记录
        6. 如果存在,则修改count
        7. 返回响应
        :param request:
        :param category_id:
        :return:
        """
        # 1. 获取分类id
        # 2. 根据分类id查询分类数据
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code":0,'errmsg':'没有次分类'})
        # 3. 获取当天日期
        from datetime import date
        today=date.today()
        # 4. 我们要查询数据库,是否存在 分类和日期 的记录
        # 精确查询
        try:
            gvc=GoodsVisitCount.objects.get(category=category,date=today)
        except GoodsVisitCount.DoesNotExist:
            # 5. 如果不存在 则新增记录
            GoodsVisitCount.objects.create(
                category=category,
                date=today,
                count=1
            )
        else:
            # 6. 如果存在,则修改count
            gvc.count += 1
            gvc.save()
        # 7. 返回响应
        return JsonResponse({"code":0,"errmsg":'ok'})

###搜索的代码##################################################

from haystack.views import SearchView

class MeiduoSearchView(SearchView):

    def create_response(self):

        # haystack 会接收 search中的请求.帮助我们对接es
        # 这个时候的数据已经获取到了
        # 在哪里呢?? context
        context = self.get_context()

        # 如何看这个数据???
        # 借助于断点 (也可以看文档)
        page = context.get('page')

        object_list=page.object_list

        data_list=[]
        #对对象列表进行遍历
        for item in object_list:
            # item.object 相当于 sku实例对象
            # item.object.id
            data_list.append({
                'id':item.object.id,
                'name':item.object.name,
                'price':item.object.price,
                'default_image_url':item.object.default_image.url,
                "searchkey": context.get('query'),          #搜索的关键字
                "page_size": context.get('paginator').num_pages,
                "count": context.get('paginator').count
            })

        return JsonResponse(data_list,safe=False)

