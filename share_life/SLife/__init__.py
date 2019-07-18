from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from config import dict_map
from logging.handlers import RotatingFileHandler
from SLife.utils.commons import ReConverter
from SLife.models import db

import logging
import redis


# 创建redis连接对象
redis_store = None

# 日志配置
# 设置日志记录的等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志文件的最大空间， 保存的日志文件个数上限
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录格式                   日志等级     输入日志信息的文件名 行数     日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚刚创建的日志记录器设置日志格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)



def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name:str 配置模式下的名字（develop, product）
    :return:
    """
    app = Flask(__name__)

    Config_class = dict_map.get(config_name)
    app.config.from_object(Config_class)

    # 指定数据库对应的app
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=Config_class.REDIS_HOST, port=Config_class.REDIS_PORT)

    # 利用flask_session ，将session保存到redis中
    # Session(app)

    # csrf防护
    # CSRFProtect(app)

    # 把自定义转换器进行注册
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from SLife import api # 避免循环导包
    app.register_blueprint(api.api, url_prefix='/api')

    return app