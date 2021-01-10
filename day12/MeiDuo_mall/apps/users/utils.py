from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def generic_user_id(user_id):
    s = Serializer(secret_key='abc', expires_in=3360)

    data = {
        'user_id': user_id
    }

    secret_data = s.dumps(data)

    return secret_data.decode()


def check_user_id(token):
    s = Serializer(secret_key='abc', expires_in=3360)
    try:
        data = s.loads(token)
    except:
        return None

    return data.get('user_id')
