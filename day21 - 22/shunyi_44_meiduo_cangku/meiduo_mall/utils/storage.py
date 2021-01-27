from django.core.files.storage import Storage

# 自定义存储类,必须继承自Storage
class QiniuStorage(Storage):

    # 存储类 要求 我们必须声明 _open 和 _save方法
    # 我们可以 把父类的 open 和 save 拷贝过来
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass


    def url(self, name):
        # name  name 其实就是 数据库中的图片的名字
        # 我们期望的图片显示 其实就是 http://七牛云外链 + 图片名字
        return 'http://qmllvum7m.hn-bkt.clouddn.com/' + name
