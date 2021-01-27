from haystack import indexes
from apps.goods.models import SKU


# 类 需要继承自 indexes.SearchIndex, indexes.Indexable

class SKUIndex(indexes.SearchIndex,indexes.Indexable):

    #属性
    # 模型很像
    text=indexes.CharField(document=True,use_template=True)
    # 每个都SearchIndex需要有一个（只有一个）字段 document=True。
    # 这向Haystack和搜索引擎都指示哪个字段是要在其中进行搜索的主要字段

    #选择document=True字段时，应在所有SearchIndex类中为该字段统一命名，以免混淆后端。惯例是命名该字段text


    # 齐思聪 我有钱 我有十万个小目标
    # 李密  (个子高,很瘦,很漂亮)
    # 李密, 张丽颖, 李柏智

    # text 是主要搜索字段  这个字段的数据 来源于 数据库中的多个字段
    # 如何设置呢???
    # text 想集成  name(商品名字),caption(副标题),id(主键) 这3个字段的数据,怎么办???
    # use_template=True
    # 就需要我们 在 指定的路径下,创建文件,来指定要对哪些字段进行检索
    """
        您需要在模板目录中创建一个名为的新模板 search/indexes/子应用名字/模型类名小写_text.txt，并将以下内容放入其中：
        
        {{ object.title }}
        {{ object.user.get_full_name }}
        {{ object.body }}
    """

    #方法
    # 要对哪个模型类进行全文检索
    def get_model(self):
        #返回类名就可以
        return SKU

    # 对哪些数据进行检索
    def index_queryset(self, using=None):

        # 返回查询结果集
        # self.get_model()  = SKU
        return  self.get_model().objects.filter(is_launched=True)
