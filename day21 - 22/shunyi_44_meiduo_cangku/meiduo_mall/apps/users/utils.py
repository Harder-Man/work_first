


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# 加密
def generic_user_id(user_id):
    # 1. 创建实例对象
    s = Serializer(secret_key='abc',expires_in=3600)
    # 2. 组织数据并加密
    data = {
        'user_id':user_id
    }
    secret_data = s.dumps(data)
    # 3. 返回
    return secret_data.decode()







from itsdangerous import BadSignature
# 解密
def check_user_id(token):

    # 1. 创建实例对象
    s = Serializer(secret_key='abc', expires_in=3600)
    # 2. 解密 捕获异常
    try:
        data = s.loads(token)
    except BadSignature:
        return None
    else:
        # 3. 返回数据
        user_id=data.get('user_id')
        return user_id

