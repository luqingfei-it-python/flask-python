from . import api
from ih.utils.response_code import RET
from ih.utils.commons import login_require
from flask import current_app, request, g, jsonify, session
from ih.utils.image_storage import storage
from ih.models import User
from ih import db
from ih import constants

@api.route("/users/avatar", methods=["POST"])
@login_require
def set_user_avatar():
    """
    设置用户头像
    参数：user_id, 图片
    :return:
    """
    # 获取保存在login_require中的g.user_id
    user_id = g.user_id
    # 提取图片
    image_file = request.files.get("avatar")
    if image_file is None:
        return jsonify(errnum=RET.PARAMERR, errmsg="未上传图片")
    image_data = image_file.read()
    # 将图片上传到七牛, 返回文件名
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.THIRDERR, errmsg="图片上传失败")
    # 把图片的地址保存到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url":file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    # 返回响应
    avatar_url = constants.QINIU_IMAGE_IP_NAME + file_name
    return jsonify(errnum=RET.OK, errmsg="OK", data={"avatar_url":avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_require
def change_user_name():
    """
    修改用户名
    参数：用户名 user_id
    :return:
    """
    # 获取参数
    user_id = g.user_id
    resp_dict = request.get_json()
    if resp_dict is None:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数不完整")
    # print(resp_dict)
    user_name = resp_dict.get("user_name")
    # 校验参数
    if user_name is None:
        return jsonify(errnum=RET.PARAMERR, errmsg="名字不能为空")
    # print(user_name)
    # 把数据保存到数据库， 并判断name是否重复（历用数据库的唯一索引）
    try:
        User.query.filter_by(id=user_id).update({"name":user_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errnum=RET.DBERR, errmsg="保存数据失败")

    # 修改session数据中的name字段
    session['name'] = user_name
    return jsonify(errnum=RET.OK, errmsg="OK", data={'name':user_name})

@api.route('/user', methods=["GET"])
@login_require
def get_user_profile():
    """获取个人信息"""
    # 获取user_id
    user_id = g.user_id
    # 查询数据库中用户的信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    # print(user.to_dict())
    # 返回数据库中用户信息
    return jsonify(errnum=RET.OK, errmsg="OK", data=user.to_dict())

@api.route("/users/auth", methods=["GET"])
@login_require
def get_user_auth():
    """获取实名认证信息"""
    # 获取user_id
    user_id = g.user_id

    # 获取真实姓名和真实身份证号码
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据查询错误")

    if user is None:
        return jsonify(errnum=RET.NODATA, errmsg="无效的操作")

    # 向前端返回数据
    return jsonify(errnum=RET.OK, errmsg="OK", data=user.auth_to_dict())

@api.route("/users/auth", methods=["POST"])
@login_require
def change_auth():
    """更改真实信息"""
    user_id = g.user_id
    # 获取参数
    resp_dict = request.get_json()
    real_name = resp_dict.get("real_name")
    id_card = resp_dict.get("id_card")

    # 校验参数的完整性
    if not all([real_name, id_card]):
        return jsonify(errnum=RET.PARAMERR, errmsg="参数不完整")

    # 把参数保存到数据库
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name":real_name, "id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")
    # 返回响应
    return jsonify(errnum=RET.OK, errmsg="OK")




