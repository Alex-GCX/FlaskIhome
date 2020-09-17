import json
import datetime
from flask import jsonify, current_app, request, g, session
from sqlalchemy.exc import IntegrityError
from . import api
from ihome import redis_connect, db, csrf
from ihome.models import Areas, Houses, HouseImages, Facilities, Orders
from ihome.utils.response_codes import RET
from ihome.utils import constants
from ihome.utils.commons import login_required, parameter_error
from ihome.utils.image_storage import storage


@api.route('/areas')
def get_areas():
    # 从缓存中获取城区信息
    try:
        areas = redis_connect.get('areas').decode()
    except Exception as e:
        current_app.logger.error(e)
        areas = None

    # 缓存中不存在则查询数据库
    if not areas:
        try:
            areas_obj_list = Areas.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取城区信息失败')
        # 将城区对象列表转换为字典
        areas_dict = {area.id: area.name for area in areas_obj_list}
        # 将字典转换为json字符串
        areas = json.dumps(areas_dict)
        # 将数据存入缓存
        try:
            redis_connect.setex('areas', constants.AREA_REDIS_EXPIRES, areas)
            print('设置areas缓存')
        except Exception as e:
            current_app.logger.error(e)

    return f'{{"errno": "0", "data": {areas}}}', 200, {'content-Type': 'application/json'}


@api.route('/houses', methods=['POST', 'PUT'])
@login_required
def create_or_update_house():
    # 接收数据
    data_dict = request.get_json()
    if not data_dict:
        return parameter_error()
    # 提取数据
    title = data_dict.get('title')
    price = data_dict.get('price')
    area_id = data_dict.get('area_id')
    address = data_dict.get('address')
    room_count = data_dict.get('room_count')
    acreage = data_dict.get('acreage')
    unit = data_dict.get('unit')
    capacity = data_dict.get('capacity')
    beds = data_dict.get('beds')
    deposit = data_dict.get('deposit')
    min_days = data_dict.get('min_days')
    max_days = data_dict.get('max_days')
    facility_ids = data_dict.get('facilities')
    house_id = data_dict.get('house_id')

    # 校验数据
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days,
             facility_ids]):
        return parameter_error()

    # 校验金额格式, 转化为两位小数
    try:
        price = round(float(price), 2)
        deposit = round(float(deposit), 2)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='金额格式有误')

    # 校验数字类型
    try:
        room_count = int(room_count)
        acreage = int(acreage)
        capacity = int(capacity)
        min_days = int(min_days)
        max_days = int(max_days)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='房屋面积/房屋数目/宜住人数/最少最多天数必须为数字')

    # area_id是否存在
    try:
        area = Areas.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取城区信息异常')
    if not area:
        return jsonify(errno=RET.PARAMERR, errmsg='城区ID不存在')

    # 最小最大入住日期
    if min_days > max_days | max_days >= 0:
        return jsonify(errno=RET.PARAMERR, errmsg='最小日期不能超过最大日期')

    # 给房屋添加设施信息

    # 第一种: 循环校验每个设施, 然后通过append添加
    # for facility_id in facility_ids:
    #     # 循环校验设施ID
    #     try:
    #         facility = Facilities.query.get(facility_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(errno=RET.DBERR, errmsg='获取设施信息异常')
    #     if not facility:
    #         return jsonify(errno=RET.DBERR, errmsg=f'设施ID"{facility_id}"不存在')
    #     # 创建房屋设置数据
    #     house.facilities.append(facility)

    # 第二种: 不循环, 通过in_(list)查询设施, 但是这样不会处理错误的设施id
    try:
        facilities = Facilities.query.filter(Facilities.id.in_(facility_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取设施信息异常')
    if not facilities:
        return jsonify(errno=RET.PARAMERR, errmsg='无有效的设施ID')

    # POST则创建新房屋对象, PUT则更新房屋
    if request.method == 'POST':
        # 创建房屋对象
        house = Houses(user_id=g.user.id, area_id=area_id, title=title, price=price, address=address,
                       room_count=room_count, acreage=acreage, unit=unit, capacity=capacity, beds=beds, deposit=deposit,
                       min_days=min_days, max_days=max_days, facilities=facilities)
    else:
        # 获取房屋对象
        try:
            house = Houses.query.get(house_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
        if not house:
            return jsonify(errno=RET.PARAMERR, errmsg='房屋ID不存在')
        # 重新设置房屋属性
        house.area_id = area_id
        house.title = title
        house.price = price
        house.address = address
        house.room_count = room_count
        house.acreage = acreage
        house.unit = unit
        house.capacity = capacity
        house.beds = beds
        house.deposit = deposit
        house.min_days = min_days
        house.max_days = max_days
        house.facilities = facilities

    # 提交房屋信息
    try:
        db.session.add(house)
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='该房屋标题已存在')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息异常')

    return jsonify(errno=RET.OK, data={'house_id': house.id})


@api.route('house/images', methods=['POST'])
@login_required
def create_house_images():
    # 获取数据, 该图片数据由浏览器提交, 不是json格式的
    image_data = request.files.get('house_image')
    house_id = request.form.get('house_id')

    # 校验数据
    if not all([image_data, house_id]):
        return parameter_error()
    # 校验房屋Id
    try:
        house = Houses.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg='房屋ID不存在')

    # 调用上传图片接口
    ret = storage(image_data)
    if ret['status'] != 200:
        # 上传失败
        return jsonify(errno=RET.THIRDERR, errmsg=f'上传失败:{ret["errmsg"]}')

    # 上传成功, 创建图片数据
    house_image = HouseImages(house=house, image_url=ret['url'])
    db.session.add(house_image)
    # 保存房屋的默认图片
    if not house.default_image_url:
        house.default_image_url = ret['url']
        db.session.add(house)
    # 提交数据
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片信息异常')

    return jsonify(errno=RET.OK, data={'url': ret['url']})


@api.route('/user/houses')
@login_required
def get_user_houses():
    """返回我的房源列表信息"""
    user = g.user
    # 获取该用户下的房屋对象列表
    try:
        house_objs = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
    # 获取房屋列表页需要展示的信息
    houses = [obj.get_list_info() for obj in house_objs]
    return jsonify(errno=RET.OK, data=houses)


@api.route('/houses/<int:house_id>')
def get_house_info(house_id):
    # 获取当前登录用户, 为空则说明未登录
    user_id = session.get('user_id', '-1')
    # 查询缓存中是否存在数据
    redis_key = f'house_info_{house_id}'
    try:
        info_json = redis_connect.get(redis_key).decode()
    except Exception as e:
        current_app.logger.error(e)
        info_json = None
    # 缓存中不存在则查询房屋信息
    if not info_json:
        try:
            house = Houses.query.get(house_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
        if not house:
            return jsonify(errno=RET.NODATA, errmsg='房屋ID不存在')
        # 获取房屋详情
        info = house.get_detail_info()
        # 将字典转为json
        info_json = json.dumps(info)
        # 存入缓存中
        redis_connect.setex(redis_key, constants.HOUSE_REDIS_EXPIRES, info_json)

    return f'{{"errno": 0, "data": {{"user_id": {user_id}, "house": {info_json}}}}}', 200, {
        'Content-Type': 'application/json'}


@api.route('/index/houses')
def get_index_houses():
    redis_key = 'index_houses'
    # 缓存中获取数据
    try:
        data_json = redis_connect.get(redis_key).decode()
    except Exception as e:
        current_app.logger.error(e)
        data_json = None
    # 不存在则查询数据库
    if not data_json:
        try:
            # 根据房屋的订购次数倒序, 取前5个房屋
            houses = Houses.query.filter(Houses.default_image_url is not None).order_by(
                Houses.order_count.desc()).limit(constants.INDEX_HOUSES_COUNT).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
        # 提取房屋标题/图片/价格
        data = [{'title': house.title, 'img_url': house.default_image_url, 'price': house.price, 'id': house.id} for
                house in houses]
        # 转化为json
        data_json = json.dumps(data)
        # 存入redis缓存中
        redis_connect.setex(redis_key, constants.INDEX_HOUSES_EXPIRES, data_json)

    return f'{{"errno": "0", "data": {data_json}}}', 200, {'Content-Type': 'application/json'}


# /search/houses?aid=12&sd=2020-08-31&ed=2020-08-31&page=1&sorted_by=new|booking|price-inc|price-des
@api.route('/search/houses')
def get_search_houses():
    # 获取查询条件
    area_id = request.args.get('aid')  # 地区ID
    start_date = request.args.get('sd')  # 起始日期
    end_date = request.args.get('ed')  # 结束日期
    page = request.args.get('page')  # 页数
    sorted_by = request.args.get('sorted_by')  # 排序

    # 先从缓存中获取结果
    redis_key = f'search_{area_id}_{start_date}_{end_date}_{sorted_by}'
    try:
        info_json = redis_connect.hget(redis_key, page).decode()
    except Exception as e:
        current_app.logger.error(e)
        info_json = None

    # 缓存不存在则查询数据库
    if not info_json:
        # 处理条件, 出现异常则认为条件为空
        # 地区ID
        try:
            area_id = int(area_id)
        except Exception as e:
            area_id = None
        # 日期
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        except Exception as e:
            return jsonify(errno=RET.PARAMERR, errmsg='日期格式错误')
        if start_date and end_date and start_date > end_date:
            return jsonify(errno=RET.PARAMERR, errmsg='起始日期不能大于终止日期')
        # 页码
        try:
            page = int(page)
        except Exception as e:
            page = 1
        # 排序
        if sorted_by not in constants.SORTED_BY:
            sorted_by = 'new'
        # 查询数据库
        # 这里的起始日期和结束日期是需要针对订单模型类Orders的起始时间和结束时间来查的, 需要排除掉在参数查询时间段内已经出租了的房源
        # 但是ORM中不太好使用子查询, 因此编写查询的思路就和包含子查询的SQL的执行过程差不多, 先执行子查询内部(查询订单表), 再执行外部(查询房屋表)

        # 先从订单模型类中查出在查询时间段内已经租出去的房屋
        # 使用列表把查询条件动态汇总起来
        filter_param = [Orders.status.in_(['WAIT_ACCEPT', 'WAIT_PAYMENT'])]
        if start_date and end_date:
            # 若条件起止日期都存在, 那么找订单的起止日期包含在条件的起止日期内的订单
            filter_param.append(start_date <= Orders.end_date)
            filter_param.append(Orders.start_date <= end_date)
        elif start_date:
            # 若条件的开始日期存在, 结束日期为空, 那么只需要找订单的结束日期不小于条件的开始日期的订单
            filter_param.append(Orders.end_date >= start_date)
        elif end_date:
            # 若条件的开始日期为空, 结束日期存在, 那么只需要找订单的开始日期不大于条件的结束日期的订单
            filter_param.append(Orders.start_date <= end_date)
            # 若条件的起止日期都为空, 那么只需要找有顾客正在入住的订单, 即状态为accepted

        # 通过拆包把查询条件拆开进行查询
        try:
            ordered_orders = Orders.query.filter(*filter_param).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取订单数据异常')
        # 获取订单的id
        ordered_house_ids = [order.house_id for order in ordered_orders]

        # 再查询房屋模型类, 把上面查到的房屋排除掉就好了
        try:
            houses_query_set = Houses.query.filter(Houses.area_id == area_id if area_id else Houses.area_id,
                                                   Houses.id.notin_(ordered_house_ids))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取房屋数据异常')

        # 排序
        if sorted_by == 'new':
            houses_query_set = houses_query_set.order_by(Houses.created_date.desc())
        elif sorted_by == 'booking':
            houses_query_set = houses_query_set.order_by(Houses.order_count.desc())
        elif sorted_by == 'price-inc':
            houses_query_set = houses_query_set.order_by(Houses.price)
        else:
            houses_query_set = houses_query_set.order_by(Houses.price.desc())

        # 分页, 把结果按每页per_page条记录进行分页, 获取第page页的分页对象pagination
        try:
            pagination = houses_query_set.paginate(page=page, per_page=constants.SEARCH_HOUSES_PAGE_COUNT)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据分页异常')
        # 获取页面数据和总页数
        houses = pagination.items
        total_page = pagination.pages

        # 提取房屋信息
        house_info = [house.get_search_info() for house in houses]
        info_dict = {'house_info': house_info, 'current_page': page, 'total_page': total_page}
        # 转为json
        info_json = json.dumps(info_dict)

        # 存入缓存中, 存在多条命令需要保持一致性, 所以使用pipeline
        try:
            # 创建pipeline对象
            pipe = redis_connect.pipeline()
            # 往管道添加命令
            pipe.hset(redis_key, page, info_json)
            pipe.expire(redis_key, constants.SEARCH_HOUSES_EXPIRES)
            # 统一执行命令
            pipe.execute()
        except Exception as e:
            current_app.logger.error(e)

    return f'{{"errno": "0", "data": {info_json}}}'


@api.route('/booking/houses/<int:house_id>')
@login_required
def get_order_house(house_id):
    # 查询房屋信息
    try:
        house = Houses.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg='房屋ID不存在')
    # 获取房屋信息
    house_info = house.get_booking_info()
    return jsonify(errno=RET.OK, data=house_info)
