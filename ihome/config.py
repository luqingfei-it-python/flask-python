import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = 'success'

    # 配置数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:wypnybz@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask_session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True # 对session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400 # 设置保存时间


class DevelopmentConfig(Config):
    """开发环境配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass

# 配置对象的映射
dict_map = {
    'develop':DevelopmentConfig,
    'product':ProductionConfig
}