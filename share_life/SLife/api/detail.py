from flask import request, jsonify, current_app

from . import api
from SLife.utils.status_code import RET
from SLife.models import Dynamic, Good, Comment, User


@api.route("/detail")
def detail():
    """详情页面"""
    dynamic_id = request.values.get("dynamic_id")

    if not dynamic_id:
        return jsonify(errnum=RET.NODATA, errmsg="没有数据")

    try:
        goods = Good.query.filter_by(dynamic_id=dynamic_id, status="true").all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    good_name_list = []
    good_count = 0
    for good in goods:
        good_name_list.append(good.username)
        good_count += 1

    try:
        comments = Comment.query.filter_by(dynamic_id=dynamic_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    try:
        dynamic = Dynamic.query.get(dynamic_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")

    if not dynamic:
        return jsonify(errnum=RET.OK, errmsg="数据不存在")

    dynamic_dict = dynamic.to_base_dict()
    dynamic_username = dynamic.user.name
    dynamic_avatar_url = dynamic.user.avatar_url
    user_info = {"username":dynamic_username, "avatar":dynamic_avatar_url}
    dynamic_user_info = dict(dynamic_dict, **user_info)

    if not comments:
        return jsonify(errnum=RET.OK, errmsg="OK", data=dynamic_user_info, data1=good_name_list, data2={"good_count": good_count})
    else:
        comment_list = []
        for comment in comments:
            user = User.query.get(comment.from_user_id)
            user_avatar = user.avatar_url
            user_name = user.name
            dict1 = {"user_avatar":user_avatar, "user_name":user_name}
            dict2 = comment.to_base_dict()
            comment_list.append(dict(dict1, **dict2))
        return jsonify(errnum=RET.OK, errmsg="OK", data=dynamic_user_info, data1=good_name_list, data2={"good_count":good_count}, data3=comment_list)
