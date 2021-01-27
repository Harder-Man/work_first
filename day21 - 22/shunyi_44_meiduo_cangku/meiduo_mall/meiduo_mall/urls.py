"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


# 注册 我们的转换器 ,告知系统
from django.urls import register_converter
from utils.converters import UsernameConverter,UUIDConverter

# 参数1: 转换器类
# 参数2: 转换器的别名
register_converter(UsernameConverter,'uc')
register_converter(UUIDConverter,'uuid')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 导入 apps.users下的urls
    #注意: 要使用 apps.xxxx
    # 因为我们的子应用 已经放到 apps包下了
    path('',include('apps.users.urls')),
    path('',include('apps.verifications.urls')),
    path('',include('apps.oauth.urls')),
    path('',include('apps.areas.urls')),
    path('',include('apps.goods.urls')),
    path('',include('apps.carts.urls')),
    path('',include('apps.orders.urls')),
    path('',include('apps.payment.urls')),

    # 美多商城管理端
    path('meiduo_admin/', include('apps.meiduo_admin.urls'),)
]
