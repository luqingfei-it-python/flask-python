from flask import request, current_app, jsonify, json, session

from SLife.utils.image_storage import storage
from SLife.utils.status_code import RET
from SLife.models import Dynamic, User
from . import api
from SLife import db, constants, redis_store


@api.route('/create_dynamic', methods=["POST"])
def create_dynamic():
    """发布新动态"""
    user_id = redis_store.get("user_id").decode()
    print(user_id)

    # 获取上传的图片文件和文字
    content = request.values.get("content")
    image_file = request.files.get("file")
    print(content)

    if all([content, image_file]):
        print("ok")
        image_data = image_file.read()
        try:
            file_name = storage(image_data)
            print(file_name)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.THIRDERR, errmsg="图片上传失败")
        dynamic = Dynamic(
            user_id=user_id,
            content=content,
            content_image_url=file_name
        )
        try:
            db.session.add(dynamic)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify(errnum=RET.OK, errmsg="OK")

    elif content:
        dynamic = Dynamic(
            user_id=user_id,
            content=content,
        )
        try:
            db.session.add(dynamic)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify(errnum=RET.OK, errmsg="OK")

    elif image_file:
        image_data = image_file.read()
        try:
            file_name = storage(image_data)
            print(file_name)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.THIRDERR, errmsg="图片上传失败")
        dynamic = Dynamic(
            user_id=user_id,
            content_image_url=file_name
        )
        try:
            db.session.add(dynamic)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify(errnum=RET.OK, errmsg="OK")

    elif not all([content, image_file]):
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")


@api.route("my_dynamic")
def my_dynamic():
    """我的动态"""
    user_id = redis_store.get("user_id").decode()

    try:
        dynamics = Dynamic.query.filter_by(user_id=user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    if not dynamics:
        return jsonify(errnum=RET.NODATA, errmsg="未查询到相关数据")

    dynamics_list = []

    for dynamic in dynamics:
        dynamics_list.append(dynamic.to_base_dict())

    user = User.query.get(user_id)
    user_list = user.to_base_dict()
    avatar_url = user_list["avatar_url"]
    name = user_list["user_name"]

    return jsonify(errnum=RET.OK, errmsg="OK", data=dynamics_list, data1={"avatar_url":avatar_url, "name":name})


@api.route("/delete")
def delete():
    """删除动态"""
    # user_id = redis_store.get("user_id").decode()

    dynamic_id = request.values.get("dynamic_id")

    if not dynamic_id:
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")

    try:
        dynamic = Dynamic.query.get(dynamic_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    if not dynamic:
        return jsonify(errnum=RET.NODATA, errmsg="操作失败")

    try:
        db.session.delete(dynamic)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="删除失败")

    return jsonify(errnum=RET.OK, errmsg="OK")