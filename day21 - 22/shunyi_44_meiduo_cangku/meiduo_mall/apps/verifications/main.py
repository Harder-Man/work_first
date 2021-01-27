from ronglian_sms_sdk import SmsSDK

accId = '8aaf07086246778ab6fe06b0'
accToken = '3b9e8ef5ec5848b483fe3f0ef0c'
appId = '8aaf0708624670f20162578206b6'

def send_message():
    # 1. 创建荣联云 实例对象
    sdk = SmsSDK(accId, accToken, appId)

    tid = '1'                           # 我们发送短信的模板,值 只能是 1 因为我们是测试用户
    mobile = '18310820688'              #'手机号1,手机号2'    给哪些手机号发送验证码,只能是测试手机号
    datas =  ('666999',5)               # ('变量1', '变量2')  涉及到模板的变量
                                        # 您的验证码为{1},请于{2} 分钟内输入
                                        # 您的验证码为666999,请于5 分钟内输入
    # 2. 发送短信
    sdk.sendMessage(tid, mobile, datas)


# 调用方法
send_message()