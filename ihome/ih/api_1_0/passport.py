from . import api
from flask import request, jsonify, current_app ,session
from ih.utils.response_code import RET
from ih import redis_store, db
from ih.models import User
from ih import constants
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import re


@api.route("/users", methods=["POST"])
def register():
    """
    用户注册
    参数： mobile , sms_code, password
    参数类型： json
    :return:
    """
    # 获取请求的json， 转换成字典
    resp_dict = request.get_json()

    # 获取参数
    mobile = resp_dict.get("mobile")
    sms_code = resp_dict.get("sms_code")
    password = resp_dict.get("password")
    password2 = resp_dict.get("password2")

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errnum=RET.PARAMERR, errmsg="参数不完整")

    if re.match(r"1[34578]\d{9}", mobile) is None:
        return jsonify(errnum=RET.PARAMERR, errmsg='手机号码错误')

    if password != password2:
        return jsonify(errnum=RET.PWDERR, errmsg="两次密码输入不一致")

    # 业务逻辑
    # 1.从redis中取出sms_code
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="读取真实短信验证码失败")

    # 3.判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errnum=RET.NODATA, errmsg="短信验证码已失效")

    # 4.删除短信验证码，防止重复使用
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 3.校验短信验证码
    real_sms_code = real_sms_code.decode()
    if sms_code != real_sms_code:
        return jsonify(errnum=RET.PARAMERR, errmsg="短语验证码错误")

    # 4.判断手机号码是否已存在
    # try:
    #     result = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errnum=RET.DBERR, errmsg='数据库异常')
    # else:
    #     if result is not None:
    #         return jsonify(errnum=RET.DATAEXIST, errmsg="手机号已存在")

    # user.password_hash = generate_password_hash(password) 一般方法对密码加密

    # 4.利用数据库错误来直接判断手机号码是否已存在
    user = User(name=mobile, mobile=mobile)
    # 保存密码
    user.password = password # 设置属性
    # 5.把数据保存到数据库
    try:
        db.session.add(user)
        db.session.commit()
    # 对抛出的异常进行区分，提取出数据相同造成的异常
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errnum=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库异常")

    # 6.使用session保存用户登录状态
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 7.返回响应
    return jsonify(errnum=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
    """
    登陆
    参数： 手机号， 密码， json
    :return:
    """
    # 获取参数
    resp_dict = request.get_json()
    mobile = resp_dict.get("mobile")
    password = resp_dict.get("password")

    # 校验参数
    if not all([mobile,password]):
        return jsonify(errnum=RET.NODATA, errmsg="数据不完整")
    # 校验手机格式
    if re.match(r"1[3578]\d{9}", mobile) is None:
        return jsonify(errnum=RET.PARAMERR, errmsg="手机格式不正确")

    # 业务逻辑处理
    # 防止暴力测试，将手机登陆次数记录在redis中
    user_ip = request.remote_addr
    try:
        # redis_store.set("access_nums_%s" % user_ip, 0)
        access_nums = redis_store.get("access_nums_%s" % user_ip)
        access_nums = int(access_nums.decode())
        print(access_nums)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and access_nums >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errnum=RET.REQERR, errmsg="请求次数过多，稍后请重试")

    # 创建模型类对象，取出数据库中数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    # 判断用户名和密码的正确性
    if user is None or user.check_password(password) is False:
        # 记录用户的登陆次数
        try:
            redis_store.incr("access_nums_%s" % user_ip, amount=1)
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errnum=RET.LOGINERR, errmsg="用户名或密码错误")

    # 保存用户登陆状态
    session["name"] = user.name
    session['mobile'] = user.mobile
    session["user_id"] = user.id

    # 返回响应
    return jsonify(errnum=RET.OK, errmsg="登陆成功")


@api.route("/session", methods=["GET"])
def check_login():
    """
    验证用户登陆状态
    :return:
    """
    # 获取保存的session
    name = session.get("name")

    # 判断name是否为空
    if name is not None:
        return jsonify(errnum=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errnum=RET.SESSIONERR, errmsg="false")

@api.route("/session", methods=["DELETE"])
def logout():
    """
    退出
    :return:
    """
    # 获取csrf_token的时候wtf时从redis中获取的，不能全部删除
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errnum=RET.OK, errmsg="退出成功")









