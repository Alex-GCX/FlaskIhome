from flask_migrate import Migrate
from ihome import create_app
from ihome import db
import logging

app = create_app('dev')

# 配置日志信息
if __name__ != '__main__':
    # 使用gunicorn启动时, 将flask应用中的日志绑定到gunicorn的日志配置中
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel('INFO')

# 创建迁移对象
migrate = Migrate(app, db)
