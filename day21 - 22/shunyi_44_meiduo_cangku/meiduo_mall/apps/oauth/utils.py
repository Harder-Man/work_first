"""
对openid进行加密和解密的操作

"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 加密
def generic_openid(openid):

    # 1. 创建一个实例对象
    # secret_key,           秘钥
    # expires_in=None       数据过期时间 单位是 秒数
    s = Serializer(secret_key='123', expires_in=3600)
    # 2.组织数据,加密数据
    data = {
        'openid': openid
    }

    secret_data = s.dumps(data)
    # 3. 返回加密数据
    # bytes --> str
    return secret_data.decode()

# 解密
from itsdangerous import BadSignature
def check_token(token):

    # 1. 创建一个实例对象
    s = Serializer(secret_key='123', expires_in=3600)
    # 2. 解密数据(异常捕获)
    try:
        data = s.loads(token)
    except BadSignature:
        return None
    # 3. 返回解密的数据
    return data.get('openid')

