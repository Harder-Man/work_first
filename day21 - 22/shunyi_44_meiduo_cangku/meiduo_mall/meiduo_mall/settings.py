"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vc)5^ocs506@g3$fvs-^o@8o7s%s_*60#3k=g=()ursshrm-_x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.meiduo.site', '127.0.0.1', '192.168.19.128']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.users',
    ##########2 注册 CORS的子应用##################
    'corsheaders',
    'apps.verifications',
    'apps.oauth',
    'apps.areas',
    'apps.contents',
    'apps.goods',
    'apps.carts',
    'apps.orders',
    'apps.meiduo_admin',
    'apps.payment',
    'django_crontab',
    'haystack',
]

MIDDLEWARE = [
    # 3 把cors的中间件 放在最上边
    # 放最上边的意思是 请求前先执行,先执行的化 就允许 8080的请求来请求 8000端口
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'mysql',  # 数据库用户密码
        'NAME': 'meiduo_mall_44'  # 数据库名字
    }
    # ,
    # 'slave': {   #从服务器
    #     'ENGINE': 'django.db.backends.mysql',
    #     'HOST': '127.0.0.1',  # 数据库主机
    #     'PORT': 8306,  # 数据库端口
    #     'USER': 'root',  # 数据库用户名
    #     'PASSWORD': 'mysql',  # 数据库用户密码
    #     'NAME': 'meiduo_mall_44'  # 数据库名字
    # }
}

# 告知系统读写分离的类 在哪里
# DATABASE_ROUTERS = ['utils.db_router.MasterSlaveDBRouter']

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

##############django-redis#######################
# CACHES 缓存的配置
CACHES = {
    "default": {  # 默认的 预留
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "code": {  # 图片验证码 和 短信验证码 使用
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 用户的浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {  # 用户的浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# SESSION_ENGINE 让我们的session保存到缓存中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS 让session保存到哪个redis的配置中
SESSION_CACHE_ALIAS = "session"

###########日志##########################################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

########################################################
"""
系统有一个 User

我们也有一个 User

现在有 2个User

系统具体只需要一个，告知系统 要使用哪个！！！
"""
# 指定本项目用户模型类
# key='子应用名.模型类名'
# 告知了系统 使用我们的!!!
AUTH_USER_MODEL = 'users.User'

##########################
# 4. CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://www.meiduo.site:8000',
    'http://127.0.0.1:8090',
    'http://localhost:8090',
    'http://www.meiduo.site:8090',
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie
# 凡是出现在白名单中的域名，都可以访问后端接口
# CORS_ALLOW_CREDENTIALS 指明在跨域访问中，后端是否支持对cookie的操作


#############邮件服务器相关的设置#############################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'qi_rui_hua@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = '123456abc'
# 收件人看到的发件人
EMAIL_FROM = '美多商城<qi_rui_hua@163.com>'

##############设置文件存储类######################################
# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'utils.storage.QiniuStorage'

##############定时任务################################################

# CRONJOBS key
#  CRONJOBS = [ (),()]
#  (参数1,参数2,参数3)
#  参数1: 频次
#       * * * * *       分别表示  分 时 日 月 周

# 参数2: 任务(函数)       路径

# 参数3: 定时任务的日志
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    (
        '*/1 * * * *', 'apps.contents.crons.generate_static_index_html',
        '>> ' + os.path.join(BASE_DIR, 'logs/crontab.log'))
]

####################################################
ALIPAY_APPID = '2016091600523030'  # 沙箱 APPID
ALIPAY_DEBUG = True  # 是否是debug模式
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱网关
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8080/pay_success.html'  # 支付成功之后的回调地址
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/app_private_key.pem')  # 美多私钥
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/alipay_public_key.pem')  # 支付宝公钥

############搜索######################################
# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',  # 搜索引擎
        'URL': 'http://192.168.19.128:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall',  # Elasticsearch建立的索引库的名称
    },
}

########### JWT #######################################
REST_FRAMEWORK = {
    # 权限
    'DEFAULT_PERMISSION_CLASSES': (
        # 先注释掉.因为我们还没登录
        # 'rest_framework.permissions.IsAuthenticated', # 必须是登录用户
    ),
    # 认证
    # 我们的认证顺序是根据 认证类的书写顺序
    # 通俗的将就是 先验证Token. 如果没有Token就验证Session
    # 我们的项目2 就是使用token
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # JWT认证
        'rest_framework.authentication.SessionAuthentication',  # session认证
        'rest_framework.authentication.BasicAuthentication',  # 测试认证
    ),
}

JWT_AUTH = {
    # 返回响应的调用方法
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'apps.meiduo_admin.utils.jwt_response_payload_handler',

    # 设置token过期时间 默认是五分钟
    # 修改为7天
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
}