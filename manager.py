from flask_migrate import Migrate
from ihome import create_app
from ihome import db
# from celery import Celery

app = create_app('dev')
# 创建celery对象
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)
# 创建迁移对象
migrate = Migrate(app, db)
