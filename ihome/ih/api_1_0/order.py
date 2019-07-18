from . import api
from ih.utils.response_code import RET
from ih.utils.commons import login_require
from flask import current_app, request, g, jsonify, session, json
from ih.utils.image_storage import storage
from ih.models import Area, User, House, Facility, HouseImage, Order
from ih import db, redis_store
from ih import constants

from datetime import datetime

@api.route("/orders", methods=["POST"])
@login_require
def save_orders():
    """保存订单数据
    参数： 房屋id：house_id
          入住时间：start_time
          离开时间：end_time
          用户id：user_id
    """
    # 获取用户id
    user_id = g.user_id
    # 获取json数据
    resp_json = request.get_json()
    # 判断参数是否存在
    if not resp_json:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    # 从json字符串中提取数据
    house_id = resp_json.get("house_id")
    start_date = resp_json.get("start_date")
    end_date = resp_json.get("end_date")

    # 判断数据完整性
    if not all([house_id, start_date, end_date]):
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    # 判断时间日期的格式是否正确
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        assert end_date >= start_date
        # 计算预定的总天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DATAERR, errmsg="日期格式错误")

    # 判断房屋是都存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询失败")
    else:
        if not house:
            return jsonify(errnum=RET.NODATA, errmsg="房屋数据不存在")

    # 防止房屋主人刷单
    if user_id == house.user_id:
        return jsonify(errnum=RET.ROLEERR, errmsg="不能预定自己的房源")
    # 确保用户在下单的时间内， 房屋没有被别人下单
    try:
        # 查询时间冲突的订单数
        counts = house.query.filter(house_id == Order.house_id, Order.begin_date <= end_date,
                                    Order.end_date >=start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="检查出错，稍后请重试")

    # 判断是否有时间冲突的订单
    if counts > 0:
        return jsonify(errnum=RET.DATAERR, errmsg="房屋已被预订")

    # 订单金额
    amount = days * house.price

    # 保存数据到数据库
    order = Order(
        user_id=user_id,
        house_id=house_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="保存数据失败")

    # 返回数据
    return jsonify(errnum=RET.OK, errmsg="OK", data={"order_id":order.id})

# /user/order?role=custom      role=landlord
@api.route("/user/orders", methods=["GET"])
@login_require
def get_user_orders():
    """获取用户自己的订单信息"""
    user_id = g.user_id

    # 获取role的内容
    role = request.args.get("role", "")

    # 判断用户要查询的自己的房源的订单还是自己提交的订单
    try:
        if role == "landlord":
            # 获取房屋主人的订单信息
            # 先查询自己有的房屋id
            houses = House.query.filter(House.user_id==user_id).all()
            houses_ids = [house.id for house in houses]

            # 在查询这些房屋被预定的有哪些
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()
        else:
            # 获取房客的订单信息
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.PARAMERR, errmsg="数据参数错误")

    # 将订单数据转换成字典格式
    order_dict_list = []
    if orders:
        for order in orders:
            order_dict_list.append(order.to_dict())

    # 返回数据
    return jsonify(errnum=RET.OK, errmsg="Ok", data={"orders":order_dict_list})

@api.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_require
def change_order_status(order_id):
    """接单，拒单"""
    user_id = g.user_id

    # 获取数据
    resp_dict = request.get_json()
    action = resp_dict.get("action")

    if not resp_dict:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    if action not in ["accept", "reject"]:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    try:
        # 获取订单，确定订单的状态必须是WAIT_ACCEPT
        order = Order.query.filter(Order.id==order_id, Order.status=="WAIT_ACCEPT").first()
        house = House.query.get(order.house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.PARAMERR, errmsg="查询数据错误")

    # 限定：房屋主人只能修改自己房屋的订单信息
    if not order or house.user_id != user_id:
        return jsonify(errnum=RET.PARAMERR, errmsg="房屋主人只能修改自己房屋订单信息")

    # 修改订单状态
    if action == "accept":
        order.status = "WAIT_PAYMENT"
    elif action == "reject":
        reason = resp_dict.get("reason")
        if not reason:
            return jsonify(errnum=RET.PARAMERR, errmsg="拒绝原因不能为空")
        order.status = "REJECTED"
        order.comment = reason

    # 把数据提交到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errnum=RET.OK, errmsg="OK")


@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_require
def save_order_comment(order_id):
    """保存用户订单的评论"""
    # 获取订单用户的id
    user_id = g.user_id

    # 获取数据
    resp_dict = request.get_json()
    comment = resp_dict.get("comment")

    # 判断comment是否存在
    if not comment:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    # 判断用户的订单是否存在， 限定用户只能操作自己的订单评论
    try:
        order = Order.query.filter(Order.user_id == user_id, Order.id == order_id, Order.status == "WAIT_COMMENT").first()
        house_id = order.house_id
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.PARAMERR, errmsg="获取订单失败")

    # 设置保存的数据
    order.status = "COMPLETE"
    order.comment = comment
    house = House.query.get(house_id)
    house.order_count += 1

    # 保存数据到数据库
    try:
        db.session.add_all([order, house])
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    # 删除保存在redis中的房屋信息
    try:
        redis_store.delete("house_info_%s" % order.house_id)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errnum=RET.OK, errmsg="OK")



