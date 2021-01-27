from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.areas.models import Area
from django.http.response import JsonResponse

class ProvienceView(View):

    def get(self,request):
        """
        1. 查询省份信息
        2. 将省份查询结果集 转换为 字典列表
        3. 返回响应
        :param request:
        :return:
        """

        #  ① 读取缓存,并判断是否存在
        from django.core.cache import cache

        province_list = cache.get('province')

        if province_list is None:
            # 如果缓存没有数据,则进行查询

            # 1. 查询省份信息
            proviencs=Area.objects.filter(parent=None)
            # 2. 将省份查询结果集 转换为 字典列表
            province_list=[]
            for item in proviencs:
                # 将字典添加到列表中
                province_list.append({
                    'id':item.id,
                    'name':item.name
                })
            #  ② 如果查询了数据库,把数据缓存
            # cache.set(key,value,有效期)
            cache.set('province',province_list,24*3600)

        # 3. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province_list})



class SubAreaView(View):

    # pk  是 前端请求的参数 是表示 上一级的id
    def get(self,request,pk):
        """
        1. 接收参数
        2. 根据 parent_id 进行查询
        3. 我们需要对查询结果集进行遍历 转换为 字典列表
        4. 返回响应
        :param request:
        :param pk:
        :return:
        """

        from django.core.cache import cache

        subs_list = cache.get('sub_area_%s'%pk)

        if subs_list is None:

            # 1. 接收参数  因为前端传递的 上一级id 在url中,所以我们在url中已经获取到了 上一级id
            #pk 就是 parent_id
            # 2. 根据 parent_id 进行查询
            subs_areas=Area.objects.filter(parent_id=pk)
            # 3. 我们需要对查询结果集进行遍历 转换为 字典列表
            subs_list = []

            for item in subs_areas:

                subs_list.append({
                    'id':item.id,
                    'name':item.name
                })

            # 添加缓存
            cache.set('sub_area_%s'%pk,subs_list,24*3600)

        # 4. 返回响应  数据格式必须是这样
        """
        {
          "code":"0",
          "errmsg":"OK",
          "sub_data":{
              "subs":[
                  {
                      "id":130100,
                      "name":"石家庄市"
                  },
                  ......
              ]
          }
        }
        """
        return JsonResponse({'code':0,
                             'errmsg':'ok',
                             'sub_data':{'subs':subs_list}})















