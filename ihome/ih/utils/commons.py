from  werkzeug.routing import BaseConverter
from flask import session, g, jsonify
from ih.utils.response_code import RET
import functools

# 定义正则转换器
class ReConverter(BaseConverter):
    """万能转换器类"""
    def __init__(self, url_map, regex):
        # 调用父类方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex

#定义登陆验证装饰器
def login_require(view_func):
    """"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")

        # 如果用户已登陆，执行视图函数
        if user_id is not None:
            # 用g来保存数据，发送给前端使用
            g.user_id = user_id
            return view_func(*args, **kwargs)
        # 未登陆，返回错误信息
        else:
            return jsonify(errnum=RET.SESSIONERR, errmsg="用户未登陆")
    return wrapper

