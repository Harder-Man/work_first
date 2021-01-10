from django.http import JsonResponse
from django.views import View
from apps.areas.models import Area

# 检查缓存
from django.core.cache import cache


class ProvinceView(View):
    def get(self, request):
        """
        1. 查询省份信息
        2. 将省份查询结果集 转换为 字典列表
        3. 返回响应
        :param request:
        :return:
        """
        # 1. 查询省份信息
        province_list = cache.get('province')

        if province_list is None:
            provinces = Area.objects.filter(parent=None)
            province_list = []

            # 2. 将省份查询结果集 转换为 字典列表
            for item in provinces:
                province_list.append({
                    'id': item.id,
                    'name': item.name
                })
            cache.set('province', province_list, 24 * 3600)

        # 3. 返回响应
        return JsonResponse({"code": 0, 'errmsg': 'ok', 'province_list': province_list})


class SubAreaView(View):

    def get(self, request, pk):
        """
        1. 接收参数
        2. 根据 parent_id 进行查询
        3. 我们需要对查询结果集进行遍历 转换为 字典列表
        4. 返回响应
        :param request:
        :param pk:
        :return:
        """
        # 1. 接收参数
        # 2. 根据 parent_id 进行查询
        subs_list = cache.get('sub_area_%s' % pk)
        if subs_list is None:
            subs_area = Area.objects.filter(parent_id=pk)
            subs_list = []

            # 3. 我们需要对查询结果集进行遍历 转换为 字典列表
            for item in subs_area:
                subs_list.append({
                    'id': item.id,
                    'name': item.name
                })
            cache.set('sub_area_%s' % pk, subs_list, 24 * 3600)
        # 4. 返回响应
        return JsonResponse({'code': 0,
                             'errmsg': "ok",
                             'sub_data': {'subs': subs_list}})
