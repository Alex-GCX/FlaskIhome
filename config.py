import redis


class BasicConfig:
    """app基础设置类"""
    SECRET_KEY = 'AKDKMAmd1235jijg9123'
    # 远程服务器
    # REMOTE_SERVER = 'alex-gcx.com'
    REMOTE_SERVER = '47.102.114.90'
    # 数据库设置
    SQLALCHEMY_DATABASE_URI = f'mysql://root:root@{REMOTE_SERVER}:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis配置
    REDIS_HOST = REMOTE_SERVER
    REDIS_PORT = 6379
    REDIS_CACHE_DB = 0  # 缓存数据库
    REDIS_SESSION_DB = 1  # session数据库
    REDIS_CELERY_DB = 2  # celery的broker
    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_SESSION_DB)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 86400  # session缓存时间, 单位:秒, 设置为1天
    # celery配置
    CELERY_BROKER_URL = f'redis://{REMOTE_SERVER}:6379/{REDIS_CELERY_DB}'
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL


class DevConfig(BasicConfig):
    """开发环境配置"""
    DEBUG = True


class ProdConfig(BasicConfig):
    """生产环境配置"""
    DEBUG = False


config_map = {
    'dev': DevConfig,
    'prod': ProdConfig
}
