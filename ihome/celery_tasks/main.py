from celery import Celery
from manager import app as flask_app

# 创建celery对象
celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
# 添加celery配置
celery.conf.update(flask_app.config)
# 自动搜索任务
celery.autodiscover_tasks(['ihome.celery_tasks.send_sms_code'])
