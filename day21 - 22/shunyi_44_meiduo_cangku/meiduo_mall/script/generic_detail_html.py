#!/usr/bin/env python

# 1. 指定当前系统的目录到 BASE_DIR 下
import sys
sys.path.insert(0, '../')

# 2. 告知系统 我们的django的配置文件在在哪里
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 3. django 文件是不能单独运行的
#  现在我就需要 单独运行  提供django 环境
import django
django.setup()

from django.template import loader
from django.conf import settings
from apps.goods import models
from utils.goods import get_breadcrumb,get_goods_specs,get_categories


def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    """
    # 获取当前sku的信息
    sku = models.SKU.objects.get(id=sku_id)

    # 查询商品频道分类
    categories = get_categories()
    # 查询面包屑导航
    breadcrumb = get_breadcrumb(sku.category)

    # 构建当前商品的规格键
    goods_specs = get_goods_specs(sku)

    # 上下文
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)

if __name__ == '__main__':
    skus = models.SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)