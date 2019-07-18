from flask import jsonify, json, request, current_app, session

from SLife.utils.status_code import RET
from SLife.models import User
from SLife import db, constants, redis_store
from . import api

@api.route("/profile")
def profile():
    """个人信息"""
    user_id = redis_store.get("user_id")
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    if user is None:
        return jsonify(errnum=RET.NODATA, errmsg="无效的操作")

    return jsonify(errnum=RET.OK, errmsg="OK", data=user.to_base_dict())


@api.route("/logout")
def logout():
    """退出"""
    redis_store.delete("user_id")
    return jsonify(errnum=RET.OK, errmsg="OK")