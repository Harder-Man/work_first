"""

加密

1. 导入
2. 创建实例对象
3. 组织数据,然后加密
"""

# 1. 导入
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# 2. 创建实例对象
# secret_key,           秘钥
# expires_in=None       数据过期时间 单位是 秒数
s = Serializer(secret_key='123', expires_in=3600)

# 3. 组织数据,然后加密
data = {
    'openid': 'abc123'
}

s.dumps(data)

#b'eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTg5Nzc5MCwiZXhwIjoxNjA5OTAxMzkwfQ.eyJvcGVuaWQiOiJhYmMxMjMifQ.rQWKP_bCTlUxlRj0xN7szmQ604Q7XV29dbWlxERFV7wrHKv-u9Ic20SvPjK8UhOlIAOA0r_ugZshUEysBGTiFA'

###################
# python manage.py shell 中测试
###################


"""
解密数据

1. 导入
2. 创建实例对象 (参数要和 加密的参数一致)
3. 解密数据
"""
# 1. 导入
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 2. 创建实例对象 (参数要和 加密的参数一致)
s = Serializer(secret_key='123',expires_in=3600)
# 3. 解密数据
# loads 的数据 也必须是 加密的
s.loads('eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTg5Nzc5MCwiZXhwIjoxNjA5OTAxMzkwfQ.eyJvcGVuaWQiOiJhYmMxMjMifQ.rQWKP_bCTlUxlRj0xN7szmQ604Q7XV29dbWlxERFV7wrHKv-u9Ic20SvPjK8UhOlIAOA0r_ugZshUEysBGTiFA')

###################
# python manage.py shell 中测试
###################



"""
解密数据的时候 有可能有异常

1. 导入
2. 创建实例对象 (参数要和 加密的参数一致)
3. 解密数据
"""
# 1. 导入
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
# 2. 创建实例对象 (参数要和 加密的参数一致)
s = Serializer(secret_key='123',expires_in=3600)
# 3. 解密数据
# loads 的数据 也必须是 加密的
try:
    s.loads('eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTg5Nzc5MCwiZXhwIjoxNjA5OTAxMzkwfQ.eyJvcGVuaWQiOiJHYmMxMjMifQ.rQWKP_bCTlUxlRj0xN7szmQ604Q7XV29dbWlxERFV7wrHKv-u9Ic20SvPjK8UhOlIAOA0r_ugZshUEysBGTiFA')
except BadSignature:
    print('加密数据被篡改了')
###################
# python manage.py shell 中测试
###################