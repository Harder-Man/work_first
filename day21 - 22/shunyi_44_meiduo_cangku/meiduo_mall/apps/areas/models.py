from django.db import models

# Create your models here.
"""

id          name        parent_id

30000       河北省       

300100      石家庄市      30000
300200      保定市        30000

300201      雄县          300200
300202      定兴县        300200


"""
from django.db import models

class Area(models.Model):
    """省市区"""
    # id
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name