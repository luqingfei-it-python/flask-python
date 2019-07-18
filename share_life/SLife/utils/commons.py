from  werkzeug.routing import BaseConverter
from flask import session, g, jsonify
import functools
import requests


# 定义正则转换器
class ReConverter(BaseConverter):
    """万能转换器类"""
    def __init__(self, url_map, regex):
        # 调用父类方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


class WeChatApi():

    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret

    def get_openid_and_session_key(self, code):
        import time
        start = time.perf_counter()
        parmas = {
            'appid': self.appid,
            'secret': self.secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }

        url = 'https://api.weixin.qq.com/sns/jscode2session'
        r = requests.get(url, params=parmas)
        openid = r.json().get('openid', '')
        session_key = r.json().get("session_key", "")
        end = time.perf_counter()
        print('获取openid用时：', end-start, '秒')

        return openid