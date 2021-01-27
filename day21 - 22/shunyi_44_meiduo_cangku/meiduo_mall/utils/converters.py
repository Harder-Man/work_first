from django.urls import converters


class UsernameConverter:

    # 正则判断
    # ^ 严格的开始
    # $ 严格的结束
    # [] 范围
    # {} 5到20个
    # 站在巨人的肩膀上
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        # value 就是验证成功之后的数据
        # 我们当前也不需要做什么
        return value


class UUIDConverter:
    # xxxxx-xxxx-xxxx-xxxx-xxx
    regex = '[\w-]+'

    def to_python(self,value):

        return value