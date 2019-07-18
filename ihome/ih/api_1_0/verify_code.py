from flask import make_response, jsonify, current_app, request

from . import api
from ih.utils.captcha.captcha import captcha
from ih.utils.response_code import RET
from ih import redis_store, db
from ih import constants
from ih.models import User
from ih.libs.yuntongxun.sms import CCP
from ih.tasks.sms.tasks import send_sms

import random


# 使用restful格式定义url
# 127.0.0.1:5000/image_code/image_code_id
@api.route('/image_code/<image_code_id>')
def image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 保存在redis中的图片验证码的id
    :return: 异常返回json字符串， 正常返回验证码图片
    """
    # 提取参数（空）
    # 检验参数（空）
    # 业务逻辑处理
    # 1.获取图片验证码信息
    # 名字   真实文本  图片数据
    name, text, image_data = captcha.generate_captcha()

    # 2. 将数据存放在redis中，redis的类型有 str , 列表 ， 哈希， set
    # str : 'id1','value'
    # 列表 : image_code:[{'':''}, '{'':''}']   读取不方便
    # 哈希 : image_code: {'id1':'value', 'id2':'value' }   删除不方便
    try:
        redis_store.set('image_code_%s' % image_code_id, text)
        redis_store.expire('image_code_%s' % image_code_id, constants.IMAGE_CODE_EXPIRE_TIME)
        # set方法和expire方法结合         记录名                     有效时间           记录值
        # redis_store.setex('image_code_%s' % image_code_id, IMAGE_CODE_EXPIRE_TIME, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg='保存图片验证码失败')


    # 返回数据
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp

# # GET /api/v1.0/sms_code/<mobile>?image_code=xxx&image_code_id=xxx
# @api.route("/sms_code/<re(r'1[34578]\d{9}'):mobile>")
# def sms_code(mobile):
#     """获取短信验证码"""
#     # 获取参数
#     image_code = request.args.get("image_code")
#     image_code_id = request.args.get("image_code_id")
#
#     # 校验参数
#     print(image_code)
#     # print(image_code_id)
#     if not all([image_code, image_code_id]):
#         # 表示参数不完整
#         return jsonify(errnum=RET.PARAMERR, errmsg="数据不完整")
#
#     # 业务逻辑处理
#     # 从redis总去取出真实的image_code
#     try:
#         real_image_code = redis_store.get("image_code_%s" % image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errnum=RET.DBERR, errmsg='redis数据库异常')
#
#     # print(real_image_code)
#
#     # 判断图片验证码是否过期
#     if real_image_code is None:
#         # 说明验证码过期
#         return jsonify(errnum=RET.NODATA, errmsg='图片验证码已失效')
#
#     # 删除图片验证码  防止重复尝试输入验证码
#     try:
#         redis_store.delete('image_code_%s' % image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#
#     # 对比用户填写的图片验证码
#     real_image_code = real_image_code.decode()
#     print(real_image_code)
#     if real_image_code.lower() != image_code.lower():
#         return jsonify(errnum=RET.DATAERR, errmsg='图片验证码错误')
#
#     # 判断发送验证码的时间是否是正常频率
#     try:
#         send_sms_code_interval = redis_store.get("send_sms_code_%s" % mobile)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if send_sms_code_interval is not None:
#             # 说明现在不能发送短信验证码
#             return jsonify(errnum=RET.REQERR, errmsg='短信验证码请求频率太高，稍后请重试')
#
#     # 判断手机号是否存在
#     try:
#         user = User.query.filter_by(mobile=mobile).first()
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if user is not None:
#         # 手机号已存在
#             return jsonify(errnum=RET.DATAEXIST, errmsg='手机号已存在')
#
#     # 不存在，生成手机验证码
#     sms_code = random.randint(100000, 999999)
#
#     # 保存真实的短信验证码
#     try:
#         redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
#         # 保存用户获取验证码记录
#         redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errnum=RET.DATAERR, errmsg='短信验证码保存失败')
#
#     # 发送短信
#     try:
#         ccp = CCP()
#         result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_EXPIRE_TIME/60)], 1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errnum=RET.THIRDERR, errmsg='发送异常')
#
#     # 返回值
#     if result == 0:
#         # 发送短信验证码成功
#         return jsonify(errnum=RET.OK, errmsg='发送成功')
#     else:
#         return jsonify(errnum=RET.THIRDERR, errmsg='发送失败')


# GET /api/v1.0/sms_code/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_code/<re(r'1[34578]\d{9}'):mobile>")
def sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    print(image_code)
    # print(image_code_id)
    if not all([image_code, image_code_id]):
        # 表示参数不完整
        return jsonify(errnum=RET.PARAMERR, errmsg="数据不完整")

    # 业务逻辑处理
    # 从redis总去取出真实的image_code
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg='redis数据库异常')

    # print(real_image_code)

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 说明验证码过期
        return jsonify(errnum=RET.NODATA, errmsg='图片验证码已失效')

    # 删除图片验证码  防止重复尝试输入验证码
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 对比用户填写的图片验证码
    real_image_code = real_image_code.decode()
    print(real_image_code)
    if real_image_code.lower() != image_code.lower():
        return jsonify(errnum=RET.DATAERR, errmsg='图片验证码错误')

    # 判断发送验证码的时间是否是正常频率
    try:
        send_sms_code_interval = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_sms_code_interval is not None:
            # 说明现在不能发送短信验证码
            return jsonify(errnum=RET.REQERR, errmsg='短信验证码请求频率太高，稍后请重试')

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
        # 手机号已存在
            return jsonify(errnum=RET.DATAEXIST, errmsg='手机号已存在')

    # 不存在，生成手机验证码
    sms_code = random.randint(100000, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
        # 保存用户获取验证码记录
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DATAERR, errmsg='短信验证码保存失败')

    # 发送短信
    # 使用celery异步发送短信
    send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_EXPIRE_TIME/60)], 1)

    # 返回值
    # 发送短信验证码成功
    return jsonify(errnum=RET.OK, errmsg='发送成功')

