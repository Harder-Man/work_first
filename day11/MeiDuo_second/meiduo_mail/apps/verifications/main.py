from ronglian_sms_sdk import SmsSDK

accId = '8aaf0708762cb1cf0176c6070ab33598'
accToken = '0508e0f81c46417fa5aa248e917effbc'
appId = '8aaf0708762cb1cf0176c6070b99359f'


def send_message():
    # 1. 创建容联云 实例对象
    sdk = SmsSDK(accId, accToken, appId)
    # 我们发送短信的模板 值只能是1
    tid = '1'
    #  给那些手机发送验证码 只能是测试手机号
    mobile = '15735404103'
    # 涉及到模板的变量---> 您的验证码为{1}， 请于{2}分钟内输入
    datas = ('666999', 5)
    # 2. 发送短信
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)
