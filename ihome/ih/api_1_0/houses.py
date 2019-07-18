from . import api
from ih.utils.response_code import RET
from ih.utils.commons import login_require
from flask import current_app, request, g, jsonify, session, json
from ih.utils.image_storage import storage
from ih.models import Area, User, House, Facility, HouseImage, Order
from ih import db, redis_store
from ih import constants

from datetime import datetime

@api.route("/areas")
def get_area():
    """获取房屋地区信息"""
    # 查询数据库信息
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # 在redis中获取到地区信息
            # print(type(resp_json))
            current_app.logger.info("hit redis area_info")
            # print(resp_json)
            resp_json = resp_json.decode()
            # print("*"*20)
            # print(resp_json)
            # print(type(resp_json))
            return resp_json, 200, {"Content-Type": "application/json"}

    try:
        area_list = Area.query.all()  # 获取到房屋地区的对象列表
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="获取房屋地区信息失败")

    # 数据处理
    area_dict_list = []
    for area in area_list:
        area_dict_list.append(area.to_dict())

    # 处理数据
    resp_dict = dict(errnum=RET.OK, errmsg="OK", data=area_dict_list)
    # print(resp_dict)
    resp_json = json.dumps(resp_dict)
    # print("*"*10)
    # print(resp_json)
    # 把数据存入redis数据库中
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REMACH_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    # 返回数据
    return resp_json, 200, {"Content-Type": "application/json"}

@api.route("/houses/info", methods=["POST"])
@login_require
def save_house_info():
    """保存房屋的信息"""
    # 获取信息
    user_id = g.user_id
    resp_dict = request.get_json()

    title = resp_dict.get("title")  # 标题
    price = resp_dict.get("price")  # 单价，单位：分
    area_id = resp_dict.get("area_id")  # 房屋区域id
    address = resp_dict.get("address")  # 地址
    room_count = resp_dict.get("room_count")  # 房间数目
    acreage = resp_dict.get("acreage")  # 房屋面积
    unit = resp_dict.get("unit")  # 房屋单元， 如几室几厅
    capacity = resp_dict.get("capacity")  # 房屋容纳的人数
    beds = resp_dict.get("beds")  # 房屋床铺的配置
    deposit = resp_dict.get("deposit")  # 房屋押金
    min_days = resp_dict.get("min_days")  # 最少入住天数
    max_days = resp_dict.get("max_days")  # 最多入住天数，0表示不限制

    # 校验参数完整性
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errnum=RET.PARAMERR, errmsg="参数不完整")

    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.PARAMERR, errmsg="参数格式错误")

    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库异常")

    if area is None:
        return jsonify(errnum=RET.NODATA, errmsg="城区信息错误")

    # 保存数据
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days,
    )
    try:
        db.session.add(house)
    except Exception as e:
        current_app.logger.error(e)

    # 获取房屋设备信息
    facility_ids = resp_dict.get("facility")

    try:
        facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    # 判断facilities中有没有数据
    if facilities:
        # 保存房屋设备信息
        house.facilities = facilities

        # 保存数据到数据库
        try:
            db.session.add(house)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

        return jsonify(errnum=RET.OK, errmsg="OK", data={"house_id": house.id})

@api.route("/houses/image", methods=["POST"])
@login_require
def save_house_image():
    """保存房屋的图片
    参数： house_id, house_image
    """
    house_image = request.files.get("house_image")
    house_id = request.form.get("house_id")

    # 判断参数完整性
    if not all([house_id, house_image]):
        return jsonify(errnum=RET.PARAMERR, errmsg="参数不完整")

    # 判断house_id的正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询错误")

    if house is None:
        return jsonify(errnum=RET.NODATA, errmsg="房屋id不存在")

    # 把图片名字保存到qiniu
    file_data = house_image.read()
    try:
        image_name = storage(file_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.THIRDERR, errmsg="图片上传失败")

    # 保存图片名到数据库中
    house_image = HouseImage(house_id=house_id, url=image_name)
    db.session.add(house_image)

    # 处理房屋的主图片
    if not house.index_image_url:
        house.index_image_url = image_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnum=RET.DBERR, errmsg="数据保存失败")

    image_url = constants.QINIU_IMAGE_IP_NAME + image_name

    return jsonify(errnum=RET.OK, errmsg="OK", data={"image_url": image_url})

@api.route("/user/houses", methods=["GET"])
@login_require
def get_user_houses():
    """获取发布的房源信息条目"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="获取数据失败")

    # 将获取的房屋信息转换成字典保存到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())

    # houses_list = json.dumps(houses_list)
    # print(houses_list)
    return jsonify(errnum=RET.OK, errmsg="OK", data=houses_list)


@api.route("/houses/index", methods=["GET"])
def get_houses_index():
    """获取主页信息"""
    # 从缓存中尝试获取信息
    try:
        resp_json = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        # 把resp_json设置为空，下面使用resp_json就不会显示未定义了
        resp_json = None
    if resp_json:
        current_app.logger.info("hit redis home_page_data")
        resp_json = resp_json.decode()
        return resp_json, 200, {"Content-Type":"application/json"}

    else:
         # 从数据库中获取订单数排名前五的home图片
        try:
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_COUNTS)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.DBERR, errmsg="房屋数据获取失败")
        if not houses:
            return jsonify(errnum=RET.NODATA, errmsg="数据不存在")

        # 用来存放房屋信息数据
        houses_list = []

        # 判断是否获取到数据
        if houses:
            for house in houses:
                if not house.index_image_url:
                    continue
                houses_list.append(house.to_basic_dict())

        # 将列表数据转换成json格式
        houses_list = dict(errnum=RET.OK, errmsg="OK", data=houses_list)
        houses_list_json = json.dumps(houses_list)

        # 将数据保存到redis数据库中
        try:
            redis_store.setex("home_page_data", constants.HOME_INDEX_IMAGE_REDIS_EXPIRES, houses_list_json)
        except Exception as e:
            current_app.logger.error(e)

        return houses_list_json, 200, {"Content-Type":"application/json"}

@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 尝试获取登陆的user_id
    # 登陆 就把user_id 返回给前端，用来判断登陆的是房主还是房客，
    # 未登录 就返回-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if house_id is None:
        return jsonify(errnum=RET.NODATA, errmsg="参数不存在")

    # 先从redis中获取数据
    try:
        house_data = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        house_data = None
    if house_data:
        current_app.logger.info("hit redis house_data")
        house_data = house_data.decode()
        return house_data, 200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="查询数据库失败")

    if house is None:
        return jsonify(errnum=RET.PARAMERR, errmsg="房屋不存在")

    # 将房屋对象数据转换成字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DATAERR, errmsg="数据出错")

    house_data = dict(errnum=RET.OK, errmsg="OK", data=house_data)
    house_data = json.dumps(house_data)

    # 将数据保存到redis数据库中
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOME_INFO_REDIS_EXPIRES, house_data)
    except Exception as e:
        current_app.logger.error(e)

    # resp_json = errnum=RET.OK, errmsg="OK", data={"house_list":houses_list}

    return house_data, 200, {"Content-Type":"application/json"}

# /api/v1.0/houses?sd=2019320&ed=2019321&aid=1s0&k=new&p=1
@api.route("/houses", methods=["GET"])
def get_house_list():
    """获取房屋列表信息（搜索页面）"""
    start_date = request.args.get("sd", "")  # 入住开始时间
    end_date = request.args.get("ed", "")  # 入住结束时间
    area_id = request.args.get("aid", "")  # 入住的区域
    sort_key = request.args.get("sk", "new")  #查询关键字
    page = request.args.get("p", 0)  # 查询页数

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.PARAMERR, errmsg="日期参数有误")

    # 判断区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errnum=RET.PARAMERR, errmsg="区域参数错误")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 获取redis中的缓存
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)  # redis中保存的键

    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            resp_json = resp_json.decode()
            current_app.logger.info("hit redis house_data")
            return resp_json, 200, {"Content-Type":"application/json"}

    # 过滤条件的参数列容器
    filter_params = []

    # 填充过滤参数
    # 时间条件
    conflict_orders = None  # 条件冲突的订单
    try:
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date, Order.begin_date <= end_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询异常")

    if conflict_orders is not None:
        # 从订单中获取冲出房屋的id
        conflict_house_id = [order.house_id for order in conflict_orders]
        if conflict_house_id:
            # 如果添加冲突房屋的id不为空， 添加查询条件
            filter_params.append(House.id.notin_(conflict_house_id))

    # 区域条件
    # 添加查询条件
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 查询数据库
    # 补充排序条件
    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:  # 新旧排序
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 处理分页
    # page对象                         当前页数            每页显示个数                           自动的错误输入
    try:
        page_obj = house_query.paginate(page=page, per_page=constants.SEARCH_HOME_PAGE_MAX_COUNTS, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnum=RET.DBERR, errmsg="数据库查询异常")

    # 获取页面数据
    house_list = page_obj.items
    houses = []
    for house in house_list:
        houses.append(house.to_basic_dict())

    # 最大页数
    total_page = page_obj.pages

    #设置缓存数据
    resp_dict = dict(errnum=RET.OK, errmsg="OK", data={"total_page":total_page, "houses":houses, "current_page":page})
    resp_json = json.dumps(resp_dict)

    if page <= total_page:
        redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)  # redis中保存的键
        # 保存数据到redis中
        try:
            # 使用pipeline 一次性执行多个redis语句防止中间发生错误
            # 创建redis管道对象
            pipeline = redis_store.pipeline()

            # 开启一次性执行多个语句的方法
            pipeline.multi()

            # 保存哈希的格式      键       字段      值
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.REDIS_CACHE_SEARCH_EXPIRES)

            # 执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type":"application/json"}























