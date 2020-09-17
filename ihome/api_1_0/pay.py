from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
from alipay.aop.api.util.SignatureUtils import verify_with_rsa
import logging
from flask import request, g, jsonify, current_app
from ihome import db
from ihome.models import Orders
from ihome.utils import constants
from ihome.api_1_0 import api
from ihome.utils.commons import login_required, RET, parameter_error


def alipay_client():
    """支付宝客户端初始化"""
    # 记录日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        filemode='a', )
    logger = logging.getLogger('')
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = constants.ALIPAY_SERVER_URL
    alipay_client_config.app_id = constants.ALIPAY_APP_ID
    alipay_client_config.app_private_key = constants.ALIPAY_PRIVATE_KEY
    alipay_client_config.alipay_public_key = constants.ALIPAY_PUBLIC_KEY
    client = DefaultAlipayClient(alipay_client_config, logger)
    return client


def alipay_model(order):
    """支付宝模型"""
    # 构造请求参数对象
    model = AlipayTradeWapPayModel()
    # 调用方系统生成的订单编号
    model.out_trade_no = order.id
    # 支付金额
    model.total_amount = str(order.amount)
    # 支付标题
    model.subject = "爱家租房"
    # 与支付宝签约的产品码名称
    model.product_code = constants.PRODUCT_CODE
    # 订单过期关闭时长（分钟）
    model.timeout_express = constants.ALIPAY_EXPRESS
    return model


def alipay_pay(client, model):
    """支付宝支付"""
    # 创建请求对象
    req = AlipayTradeWapPayRequest(biz_model=model)
    # 设置回调通知地址（GET）, 用户浏览器直接访问该地址
    req.return_url = constants.ALIPAY_RETURN_URL
    # 设置回调通知地址（POST）, 支付宝会请求该地址, 用户看不到
    # req.notify_url = constants.ALIPAY_NOTIFY_URL
    # 执行API调用,获取支付连接
    pay_url = client.page_execute(req, http_method='GET')
    return pay_url


@api.route('/orders/alipay', methods=['POST', 'PATCH'])
@login_required
def handle_alipay():
    if request.method == 'POST':
        # 创建支付订单
        return create_alipay()
    else:
        # 更新订单信息
        return change_order()


def create_alipay():
    # 接收数据
    data_dict = request.get_json()
    if not data_dict:
        return parameter_error()
    # 提取数据
    order_id = data_dict.get('order_id')
    if not order_id:
        return parameter_error()
    # 校验order_id
    try:
        order = Orders.query.get(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    if not order:
        return jsonify(errno=RET.PARAMERR, errmsg='订单ID不存在')
    # 判断订单是否属于当前用户
    if order.user != g.user:
        return jsonify(errno=RET.PARAMERR, errmsg='该订单不属于当前用户')
    # 调用支付接口
    try:
        client = alipay_client()
        model = alipay_model(order)
        pay_url = alipay_pay(client, model)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='调用支付接口异常')
    return jsonify(errno=RET.OK, data={'url': pay_url})


def check_signature(params):
    """验证签名"""
    # 取出签名
    sign = params.pop('sign')
    # 取出签名类型
    params.pop('sign_type')
    # 取出字典的value, 并对字典按key的字母升序排序, 得到新的列表
    params = sorted(params.items(), key=lambda x: x[0], reverse=False)
    # 将列表转换为二进制字符串
    message = '&'.join(f'{k}={v}' for k, v in params).encode()
    # 验证
    try:
        result = verify_with_rsa(constants.ALIPAY_PUBLIC_KEY.encode('utf-8').decode('utf-8'), message, sign)
        return result
    except Exception as e:
        current_app.logger.error(e)
        return False


def change_order():
    """支付完成后修改状态"""
    # 接收数据
    print(type(request.form))
    data_dict = request.form.to_dict()
    if not data_dict:
        return parameter_error()
    # 校验签名
    if not check_signature(data_dict):
        return jsonify(errno=RET.PARAMERR, errmsg='数据验证失败')
    # 获取订单编号和支付宝编号
    order_id = data_dict.get('out_trade_no')
    trade_no = data_dict.get('trade_no')
    # 更新状态, 限制该订单状态为'待接单', 订单的提交人为当前登录用户
    try:
        order = Orders.query.get(order_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取订单异常')
    # 校验订单
    if not order:
        return jsonify(errno=RET.PARAMERR, errmsg='订单ID不存在')
    if order.status != 'WAIT_PAYMENT':
        return jsonify(errno=RET.PARAMERR, errmsg='订单状态不为"待支付"')
    if order.user != g.user:
        return jsonify(errno=RET.PARAMERR, errmsg='该订单不属于当前用户')
    # 更新订单
    order.status = 'WAIT_COMMENT'
    order.trade_no = trade_no
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='更新订单异常')

    return jsonify(errno=RET.OK)
