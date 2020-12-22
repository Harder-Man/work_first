from django.db import models


# Create your models here.

class BookInfo(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class PeopleInfo(models.Model):
    name = models.CharField(max_length=10)
    gender = models.BooleanField()
    book = models.ForeignKey(BookInfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# class BookInfo(models.Model):
#     name = models.CharField(max_length=10)
#
#
# # 人物
# class PeopleInfo(models.Model):
#     # name
#     name = models.CharField(max_length=10)
#     # gender 性别
#     gender = models.BooleanField()
#
#     # book 外键
#     # 外键的级联关系
#     # 外检的相关知识
#     book = models.ForeignKey(BookInfo, on_delete=models.CASCADE)
