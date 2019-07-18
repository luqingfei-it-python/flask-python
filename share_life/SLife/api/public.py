from flask import current_app,jsonify, request, json, session

from SLife.utils.commons import WeChatApi
# from SLife.utils.WXBizDataCrypt import WXBizDataCrypt
from SLife.models import User, Dynamic, Good, Comment
from . import api
from SLife import db, constants, redis_store
from SLife.utils.status_code import RET


@api.route("/get_userinfo", methods=["POST"])
def get_userinfo():
    """获取授权信息"""
    # 获取数据
    code = request.values.get("code")
    # encrypteData = request.values.get("encrypteData")
    # iv = request.values.get("iv")

    # 获取userinfo对象并转换成str格式
    userinfo = request.values.get("userinfo")
    userinfo = json.loads(userinfo)

    username = userinfo.get("nickName")
    avatar_url = userinfo.get("avatarUrl")
    gender = userinfo.get("gender")
    gender = int(gender)
    province = userinfo.get("province")
    city = userinfo.get("city")
    # 校验参数完整性
    if not all([code, username, avatar_url, gender, province, city]):
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")

    print(code)

    # 获取openid
    try:
        wechatapi = WeChatApi(constants.APPID, constants.SECRET_KEY)
        openid = wechatapi.get_openid_and_session_key(code)
        # session_key = wechatapi.get_openid_and_session_key(code).get("session_key")
        # 解码openid
        # pc = WXBizDataCrypt(constants.APPID, session_key)
        # result = pc.decrypt(encrypteData, iv)
        # print(result["openid"])
        print(type(openid))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.THIRDERR, errmsg="openid获取失败")


    # 判断授权的用户是否已经在数据库中
    try:
        user = User.query.filter_by(openid=openid).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    # 判断有没有数据
    if user:
        print("111")
        try:
            User.query.filter_by(openid=openid).update({"name":username, "avatar_url":avatar_url, "gender":gender, "province":province, "city":city})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

        # 设置user_id
        # session["user_id"] = user1.first().id
        try:
            redis_store.setex("user_id", constants.USER_ID_EXPIRES, user.id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.DATAERR, errmsg="user_id保存失败")

        return jsonify(errnum=RET.OK, errmsg="OK")
    else:
        # 把获取到的数据放入数据库
        print("2")
        user2 = User(
            name=username,
            avatar_url=avatar_url,
            gender=gender,
            province=province,
            city=city,
            openid=openid,
        )
        try:
            db.session.add(user2)
            db.session.commit()
            print(3)
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

        # 设置user_id
        # session["user_id"] = user2.id
        try:
            redis_store.setex("user_id", constants.USER_ID_EXPIRES, user2.id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.DATAERR, errmsg="user_id保存失败")
        return jsonify(errnum=RET.OK, errmsg="OK")


@api.route("/public", methods=["GET"])
def get_public():
    """公屏"""
    # 获取session中的user_id
    user_id = redis_store.get("user_id").decode()

    try:
        dynamics = Dynamic.query.order_by(Dynamic.id.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="查询数据失败")
    dynamics_user_good_list = []

    if dynamics:
        for dynamic in dynamics:
            user = User.query.get(dynamic.user_id)
            good = Good.query.filter_by(dynamic_id=dynamic.id, user_id=user_id).first()
            if good is None:
                dict1 = user.to_base_dict()
                dict2 = dynamic.to_base_dict()
                dict3 = {"status": "false"}
                dynamics_user_good_list.append(dict(dict(dict1, **dict2), **dict3))
            else:
                dict1 = user.to_base_dict()
                dict2 = dynamic.to_base_dict()
                dict3 = good.to_base_dict()
                dynamics_user_good_list.append(dict(dict(dict1, **dict2), **dict3))

    user = User.query.get(user_id)
    user_list = user.to_base_dict()
    # print(user_list)

    return jsonify(errnum=RET.OK, errmsg="OK", data=dynamics_user_good_list, data1=user_list)


@api.route("dynamic_comment", methods=["POST"])
def get_comment():
    """评论"""
    user_id = redis_store.get("user_id").decode()

    comment = request.values.get("comment")
    dynamic_id = request.values.get("dynamic_id")

    if not all([comment, dynamic_id]):
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")
    print("1")

    comment = Comment(
        dynamic_id=dynamic_id,
        content=comment,
        from_user_id=user_id
    )

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errnum=RET.OK, errmsg="OK", data={"comment_id": comment.id})


@api.route("/get_other")
def get_other():
    """他人更圈历史"""
    user_id = redis_store.get("user_id").decode()
    other_id = request.values.get("other_id")

    if not other_id:
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")

    try:
        dynamics = Dynamic.query.filter_by(user_id=other_id).order_by(Dynamic.id.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="查询数据失败")
    dynamics_user_good_list = []

    if dynamics:
        for dynamic in dynamics:
            user = User.query.get(other_id)
            good = Good.query.filter_by(dynamic_id=dynamic.id, user_id=user_id).first()
            if good is None:
                dict1 = {"avatar_url":user.to_base_dict().get("avatar_url"), "user_name":user.to_base_dict().get("user_name")}
                dict2 = dynamic.to_base_dict()
                dict3 = {"status": "false"}
                dynamics_user_good_list.append(dict(dict(dict1, **dict2), **dict3))
            else:
                dict1 = {"avatar_url":user.to_base_dict().get("avatar_url"), "user_name":user.to_base_dict().get("user_name")}
                dict2 = dynamic.to_base_dict()
                dict3 = good.to_base_dict()
                dynamics_user_good_list.append(dict(dict(dict1, **dict2), **dict3))

    return jsonify(errnum=RET.OK, errmsg="OK", data=dynamics_user_good_list)
