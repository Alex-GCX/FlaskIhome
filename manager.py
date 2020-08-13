from flask_migrate import Migrate
from ihome import create_app
from ihome import db

app = create_app('dev')
# 创建迁移对象
migrate = Migrate(app, db)
