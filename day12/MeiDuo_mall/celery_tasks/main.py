from celery import Celery

app = Celery(main='MeiDuo')

app.config_from_object('celery_tasks.config')

app.autodiscover_tasks(['celery_tasks.sms_tasks'])
