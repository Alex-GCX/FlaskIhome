from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis

app = Flask(__name__)


class AppConfig:
    """app设置类"""
    DEBUG = True
    SECRET_KEY = 'akdkmamd1235jijg9123'
    # 远程服务器
    REMOTE_SERVER = 'alex-gcx.com'
    # 数据库设置
    SQLALCHEMY_DATABASE_URI = f'mysql://root:root@{REMOTE_SERVER}:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis配置
    REDIS_HOST = REMOTE_SERVER
    REDIS_PORT = 6379
    REDIS_CACHE_DB = 0  # 缓存数据库
    REDIS_SESSION_DB = 1  # session数据库
    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_SESSION_DB)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 86400  # session缓存时间, 单位:秒, 设置为1天


# 应用添加配置
app.config.from_object(AppConfig)
# 创建数据库链接
db = SQLAlchemy(app)
redis_connect = redis.StrictRedis(host=AppConfig.REDIS_HOST, port=AppConfig.REDIS_PORT, db=AppConfig.REDIS_DB)
# 创建session对象
session = Session(app)
# 创建迁移对象
migrate = Migrate(app, db)
# 启用CSRF模块
CSRFProtect(app)
