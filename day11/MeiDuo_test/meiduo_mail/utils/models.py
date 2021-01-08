from django.db import models

"""
我们想 以后的表中 每个表都有这两个字段 分别是 create_time 和 update_time 
这个时候我们用 面对对象 的方法
"""

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True  # 说明是抽象模型类 用于继承使用, 数据库迁移时 不会创建BaseModels的表
