from celery import Celery

app = Celery(main='meiduo')

app.config_from_object('Celery_tasks.config')

app.autodiscover_tasks(['Celery_tasks.sms'])
app.autodiscover_tasks(['Celery_tasks.emails'])