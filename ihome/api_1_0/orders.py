from flask import request, g, jsonify, current_app
from datetime import datetime
from ihome import db
from ihome.api_1_0 import api
from ihome.models import Orders, Houses
from ihome.utils.commons import login_required, parameter_error, RET


@api.route('/orders', methods=['POST', 'GET'])
@login_required
def handle_orders():
    """处理订单"""
    if request.method == 'POST':
        return create_order()
    else:
        return get_orders()


# 创建订单
def create_order():
    """创建订单"""
    # 接收数据
    data_dict = request.get_json()
    if not data_dict:
        return parameter_error()
    # 提取数据
    house_id = data_dict.get('house_id')
    start_date = data_dict.get('start_date')
    end_date = data_dict.get('end_date')

    # 校验数据
    if not all([house_id, start_date, end_date]):
        return parameter_error()

    # 校验日期
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='日期格式错误')

    # 计算共几晚
    days = (end_date - start_date).days
    if days < 0:
        return jsonify(errno=RET.PARAMERR, errmsg='起始日期不能超过结束日期')

    for i in range(5):
        # 校验house_id
        try:
            # .with_for_update添加悲观锁
            # house = Houses.query.filter_by(id=house_id).with_for_update().first()
            # 乐观锁方式
            house = Houses.query.get(house_id)
            # print(f'{g.user.name}-a-{house.order_count}')
            # time.sleep(3)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取房屋信息异常')
        if not house:
            return jsonify(errno=RET.PARAMERR, errmsg='房屋ID不存在')
        # 校验房东不能订购自己的房屋
        if g.user.id == house.user_id:
            return jsonify(errno=RET.PARAMERR, errmsg='不能预定自己的房屋')
        # 保存老的房屋订单数量
        old_order_count = house.order_count
        # 计算总价
        amount = days * house.price

        # 查看该房屋该时间段是否有预定
        try:
            count = Orders.query.filter(Orders.house_id == house_id, start_date <= Orders.end_date,
                                        Orders.start_date <= end_date,
                                        Orders.status.in_(['WAIT_ACCEPT', 'WAIT_PAYMENT'])).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取订单信息异常')
        if count > 0:
            return jsonify(errno=RET.DATAEXIST, errmsg='该时间段已被订购')

        # 创建订单
        order = Orders(user=g.user, house=house, start_date=start_date, end_date=end_date, days=days, price=house.price,
                       amount=amount)
        db.session.add(order)

        # 房屋订单数量加1, 避免同时下单, 使用乐观锁
        new_house = Houses.query.filter(Houses.id == house_id, Houses.order_count == old_order_count).update(
            {Houses.order_count: old_order_count + 1})
        # house.order_count += 1
        if new_house:
            db.session.add(house)
            # time.sleep(3)
            # print(f'{g.user.name}-b-{house.order_count}')
            try:
                db.session.commit()
                # time.sleep(3)
                # print(f'{g.user.name}-c-{house.order_count}')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg='创建订单异常')
            return jsonify(errno=RET.OK)
        else:
            db.session.rollback()

    return jsonify(errno=RET.DBERR, errmsg='该房屋已被预定')


def get_orders():
    """查询订单"""
    # 获取url参数, 当前角色
    role = request.args.get('role', 'my')
    # 获取订单数据
    try:
        if role == 'my':
            # 我的订单
            orders = Orders.query.filter_by(user=g.user).order_by(Orders.id.desc()).all()
        else:
            # 客户订单
            # 获取我的房屋
            house_ids = [house.id for house in g.user.houses]
            # 获取我的房屋下的订单
            orders = Orders.query.filter(Orders.house_id.in_(house_ids)).order_by(Orders.id.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    # 获取返回的订单信息
    order_info = [order.get_list_info() for order in orders]

    return jsonify(errno=RET.OK, data=order_info)


@api.route('/orders/accept/<int:order_id>', methods=['PATCH'])
@login_required
def accept_order(order_id):
    """接收/拒绝订单"""
    # 接收数据
    data_dict = request.get_json()
    if not data_dict:
        return parameter_error()
    # 获取对应的操作和评论信息
    action = data_dict.get('action')
    comment = data_dict.get('comment')
    if not action:
        return parameter_error()
    # 更新状态, 限制该订单状态为'待接单', 订单的房源为当前登录用户的房源
    try:
        order = Orders.query.get(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    # 校验订单
    if not order:
        return jsonify(errno=RET.PARAMERR, errmsg='订单ID不存在')
    if order.status != 'WAIT_ACCEPT':
        return jsonify(errno=RET.PARAMERR, errmsg='订单状态不为"待接单"')
    if order.house.user != g.user:
        return jsonify(errno=RET.PARAMERR, errmsg='订单房屋不属于当前用户')
    # 判断状态
    if action == 'accept':
        status = 'WAIT_PAYMENT'
    elif action == 'reject':
        status = 'REJECTED'
    else:
        return jsonify(errno=RET.PARAMERR, errmsg='无效的操作')
    # 更新订单
    order.status = status
    order.comment = comment
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='更新订单异常')

    return jsonify(errno=RET.OK)


@api.route('/orders/comment/<int:order_id>', methods=['PATCH'])
@login_required
def comment_order(order_id):
    """评论订单"""
    # 接收数据
    data_dict = request.get_json()
    if not data_dict:
        return parameter_error()
    # 提取数据
    comment = data_dict.get('comment')
    if not comment:
        return parameter_error()
    # 校验订单ID
    try:
        order = Orders.query.get(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    # 校验订单
    if not order:
        return jsonify(errno=RET.PARAMERR, errmsg='订单ID不存在')
    if order.status != 'WAIT_COMMENT':
        return jsonify(errno=RET.PARAMERR, errmsg='订单状态不为"待评价"')
    if order.user != g.user:
        return jsonify(errno=RET.PARAMERR, errmsg='该订单不属于当前用户')
    # 更新订单
    order.comment = comment
    order.status = 'COMPLETED'
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='更新订单异常')
    return jsonify(errno=RET.OK)


@api.route('/orders/cancel/<int:order_id>', methods=['PATCH'])
@login_required
def cancel_order(order_id):
    """取消订单"""
    # 校验订单ID
    try:
        order = Orders.query.get(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    # 校验订单
    if not order:
        return jsonify(errno=RET.PARAMERR, errmsg='订单ID不存在')
    if order.status not in ['WAIT_ACCEPT', 'WAIT_PAYMENT']:
        return jsonify(errno=RET.PARAMERR, errmsg='订单状态不为"待接单"或"待支付"')
    if order.user != g.user:
        return jsonify(errno=RET.PARAMERR, errmsg='该订单不属于当前用户')
    # 更新订单
    order.status = 'CANCELLED'
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='更新订单异常')
    return jsonify(errno=RET.OK)
