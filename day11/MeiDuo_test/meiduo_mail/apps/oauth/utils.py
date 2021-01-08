from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def generic_openid(openid):
    s = Serializer(secret_key='abc', expires_in=3360)
    data = {
        'openid':openid
    }
    secret_data = s.dumps(data)

    return secret_data.decode()

def check_openid(token):
    s = Serializer(secret_key='abc', expires_in=3360)

    try:
        data = s.loads(token)
    except:
        return None

    return data.get('openid')
