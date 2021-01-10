from celery import Celery

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

app = Celery(main='MeiDuo')

app.config_from_object('celery_tasks.config')

app.autodiscover_tasks(['celery_tasks.sms_tasks'])

app.autodiscover_tasks(['celery_tasks.email_tasks'])
