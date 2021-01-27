from django.db import models

"""
我们想 以后的 表 ,每个表中 都有2个字段 分别是  create_time  和 update_time
这个时候 我们可以采用 面向对象的 继承来实现

我们定义一个基类 ,基类中有这2个字段

子类继承我们的基类. 

"""

class BaseModel(models.Model):
    """为模型类补充字段"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表