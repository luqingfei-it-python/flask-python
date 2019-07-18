from flask import Blueprint

# 创建蓝图对象
api = Blueprint('api_1_0', __name__)


# 把试图函数导入进来
from . import demo, verify_code, passport, profile, houses, order, pay
