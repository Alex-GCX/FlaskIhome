import json
from flask import jsonify, current_app, request, g
from sqlalchemy.exc import IntegrityError
from . import api
from ihome import redis_connect, db, csrf
from ihome.models import Areas, Houses, HouseImages, Facilities
from ihome.utils.response_codes import RET
from ihome.utils import constants
from ihome.utils.commons import login_required, parameter_error
from ihome.utils.image_storage import storage


@api.route('/areas')
def get_areas():
    # 从缓存中获取城区信息
    try:
        areas = redis_connect.get('areas')
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

    return areas, 200, {'content-Type': 'application/json'}


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
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, facility_ids]):
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
    try:
        house_image = HouseImages(house=house, image_url=ret['url'])
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片信息异常')

    return jsonify(errno=RET.OK, data={'url': ret['url']})
