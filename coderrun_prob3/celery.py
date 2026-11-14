import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderrun_prob3.settings')

app = Celery('coderrun_prob3')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
