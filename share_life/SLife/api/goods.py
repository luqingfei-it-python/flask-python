from flask import request, current_app, jsonify, json, session

from SLife.utils.status_code import RET
from SLife.models import Dynamic, Good, User
from . import api
from SLife import db, constants, redis_store

@api.route("/goods")
def get_good():
    """点赞"""
    user_id = redis_store.get("user_id").decode()
    dynamic_id = request.values.get("dynamic_id")
    if not dynamic_id:
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    goods = Good.query.filter_by(dynamic_id=dynamic_id, user_id=user.id).first()
    if not goods:
        goods = Good(
            dynamic_id=dynamic_id,
            username=user.name,
            user_id=user.id,
            status="true"
        )

    else:
        goods = Good.query.filter_by(dynamic_id=dynamic_id, user_id=user.id).update({"username":user.name, "status":"true"})

    try:
        db.session.add(goods)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errnum=RET.OK, errmsg="OK")
