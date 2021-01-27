"""

Celery 实现了 生产者 消费者设计模式

4个人

Celery:		实现了 生产者 消费者设计模式                     v

生产者:		         生成任务（函数）                       v

消息队列(broker)：	队列的作用                            v

消费者：	            执行任务（函数）                        v

    通过指令来消费(执行)任务(函数)
    虚拟环境下 celery -A celery实例对象的文件路径  worker -l INFO

    celery -A celery_tasks.main worker -l INFO

"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')


from celery import Celery

# 1. 创建celery 实例

# celery 的第一个参数  main 其实就是一个名字
# 这个名字 一般我们使用 任务的名字 (随便起 没有什么作用)
app=Celery(main='meiduo')


# 2. 加载celery的配置信息
# 配置信息中 指定了 我们的broker (消息队列)
# 我们选择 redis作为消息队列(broker)
# 我们把 broker 的配置 单独放到一个文件中,让celery加载这个文件
# 因为 以后还有可能有其他的配置,所以我们最好 单独创建一个配置文件

app.config_from_object('celery_tasks.config')


# 补充#任务包的任务需要celery调用自检检查函数(在main.py里写)
# app.autodiscover_tasks([])
###################必须注意 tasks(列表)

# 元素是 字符串,就是 任务的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])












