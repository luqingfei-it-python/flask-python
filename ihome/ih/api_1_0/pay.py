from . import api
from ih.utils.response_code import RET
from ih.utils.commons import login_require
from flask import current_app, request, g, jsonify, session, json
from ih.utils.image_storage import storage
from ih.models import Area, User, House, Facility, HouseImage, Order
from ih import db, redis_store
from ih import constants
from alipay import AliPay
import os

@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_require
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id

    # 判断用户操作的订单是否存在， 是不是自己的订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    if not order:
        return jsonify(errnum=RET.PARAMERR, errmsg="参数错误")

    # 创建支付宝sdk工具对象
    alipay = AliPay(
        appid="2016092800615040",
        app_notify_url=None,  # the default notify path
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # alipay public key, do not use your own public key!
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",  # RSA or RSA2
        debug = True  # False by default
    )

    # 手机网站支付, open this url in your browser:https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order_id,  # 订单编号
        total_amount=str(order.amount/100),  # 订单价格
        subject="ihome %s" % order_id,  # 订单标题
        return_url="http://127.0.0.1:5000/payComplete.html",  # 付款结束返回的页面
        notify_url=None  # this is optional
    )

    # 构建用户跳转的支付链接地址
    pay_url = constants.ALIPAY_PREFIX_URL + order_string

    return jsonify(errnum=RET.OK, errmsg="OK", data={"pay_url": pay_url})

@api.route("/order/payment", methods=["PUT"])
@login_require
def save_pay_result():
    """保存订单支付结果"""
    # 获取数据
    alipay_data = request.form.to_dict()

    # 提取支付宝签名参数sign，并保留其他数据
    alipay_sign = alipay_data.pop("sign")

    # 创建支付宝sdk工具对象
    alipay = AliPay(
        appid="2016092800615040",
        app_notify_url=None,  # the default notify path
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # alipay public key, do not use your own public key!
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",  # RSA or RSA2
        debug=True  # False by default
    )

    # 借助工具验证参数的合法性
    # 如果正确返回true， 错误返回false
    print(alipay_data)
    print("*"*20)
    print(alipay_sign)
    result = alipay.verify(alipay_data, alipay_sign)

    print(result)
    # 修改数据库中订单信息
    if not result:
        order_id = alipay_data.get("out_trade_no")
        trade_no = alipay_data.get("trade_no")
        print("OK")
        try:
            Order.query.filter(Order.id==order_id).update({"status":"WAIT_COMMENT", "trade_no":trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errnum=RET.OK, errmsg="OK")




