from flask import request, jsonify, current_app, session, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from . import api
from ihome import redis_connect, db
from ihome.utils.response_codes import RET
from ihome.utils import constants
from ihome.models import Users
from ihome.utils.commons import login_required, parameter_error
from ihome.utils.image_storage import storage
import re


# 注册
# @csrf.exempt
@api.route('/users', methods=['POST'])
def register():
    # 接收数据
    dict_data = request.get_json()
    if not dict_data:
        return parameter_error()
    # 提取数据
    phone = dict_data.get('mobile')
    sms_code = dict_data.get('phoneCode')
    password = dict_data.get('password')
    password2 = dict_data.get('password2')

    # 校验数据
    if not all([phone, sms_code, password, password2]):
        return parameter_error()

    # 两次密码是否一致
    if password2 != password:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    # 校验手机号
    if not re.match(r'1[^120]\d{9}', phone):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    # 验证短信验证码
    sms_code_key = f'sms_code_{phone}'
    # 获取真实短信验证码
    try:
        real_sms_code = redis_connect.get(sms_code_key)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取redis验证码异常')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码不存在或已过期')
    if sms_code != real_sms_code.decode():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码不正确')

    # 创建用户
    user = Users(phone=phone, password=password, name=phone)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已注册过用户')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='创建用户异常')

    # 注册则认为已经登录, 设置session，记录登录状态
    session['user_id'] = user.id
    session['phone'] = phone
    session['name'] = phone

    return jsonify(errno=RET.OK)


# 登录/登出
# @csrf.exempt
@api.route('/sessions', methods=['GET', 'POST', 'DELETE'])
def handle_sessions():
    if request.method == 'POST':
        # 登录
        return login()
    elif request.method == 'DELETE':
        # 登出
        return logout()
    else:
        # 获取当前登录用户
        return get_login_user()


def login():
    """登录"""
    # 接收数据
    post_dict = request.get_json()
    if not post_dict:
        return parameter_error()
    # 提取数据
    phone = post_dict.get('phone')
    password = post_dict.get('password')

    # 校验数据
    if not all([phone, password]):
        return parameter_error()

    # 限制同一手机号一分钟内只能登陆5次
    his_login_key = f'his_login_{phone}'
    try:
        # incr增加记录的次数，若不存在该key则会创建并默认值为1
        count = redis_connect.incr(his_login_key)
        if int(count) > constants.USER_LOGIN_COUNT:
            return jsonify(errno=RET.REQERR, errmsg='一分钟内只能登录5次')
        redis_connect.expire(his_login_key, constants.USER_LOGIN_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取登录记录异常')

    # 校验是否已经登录过
    print(session)
    if phone in session.values():
        return jsonify(errno=RET.OK)

    # 校验手机号是否注册过
    try:
        user = Users.query.filter_by(phone=phone).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息异常')
    # 将用户名错误和密码错误放在一起返回，不要返回地太细节
    if not user or not user.check_password_hash(password):
        return jsonify(errno=RET.PWDERR, errmsg='用户名或密码不正确')

    # 记录登录session
    session['user_id'] = user.id
    session['name'] = user.name
    session['phone'] = phone

    return jsonify(errno=RET.OK)


def logout():
    """登出"""
    # 判断是否登录过
    if not session.get('user_id'):
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')
    # 清除session
    session.pop('user_id')
    session.pop('name')
    session.pop('phone')

    return jsonify(errno=RET.OK)


def get_login_user():
    """获取登录用户"""
    # 判断是否登录过
    name = session.get('name')
    if name:
        return jsonify(errno=RET.OK, data={'name': name})
    return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')


@api.route('/user/info')
@login_required
def get_user_info():
    """获取用户信息接口"""
    user = g.user
    return jsonify(errno=RET.OK, data={'url': user.image_url, 'name': user.name, 'mobile': user.phone})


@api.route('/user/images', methods=['PATCH'])
@login_required
def set_user_image():
    """设置用户头像"""
    # 获取传入的图片
    image_data = request.files.get('avatar')
    if not image_data:
        return parameter_error()
    # 调用存储接口
    resp = storage(image_data)
    if resp['status'] != 200:
        # 存储失败
        return jsonify(errno=RET.THIRDERR, errmsg=resp['errmsg'])
    # 存储成功, 更新数据库的url
    g.user.image_url = resp['url']
    try:
        db.session.add(g.user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户头像异常')

    return jsonify(errno=RET.OK, data={'url': resp['url']})


@api.route('/user/names', methods=['PATCH'])
@login_required
def set_user_name():
    """设置用户名称接口"""
    # 接受数据
    dict_data = request.get_json()
    if not dict_data:
        return parameter_error()
    # 提取数据
    name = dict_data.get('name')
    if not name:
        return parameter_error()
    # 设置用户名
    g.user.name = name
    try:
        db.session.add(g.user)
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='该用户名已存在')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户名异常')

    # 修改session的值
    session['name'] = name

    return jsonify(errno=RET.OK)


@api.route('user/auth', methods=['GET', 'PATCH'])
@login_required
def handle_auth():
    """实名认证接口"""
    if request.method == 'GET':
        return get_user_auth()
    else:
        return authenticate()


def get_user_auth():
    return jsonify(errno=RET.OK, data={'real_name': g.user.real_name, 'real_id_card': g.user.real_id_card})


def authenticate():
    # 接收数据
    dict_data = request.get_json()
    if not dict_data:
        return parameter_error()
    # 提取数据
    real_name = dict_data.get('real_name')
    real_id_card = dict_data.get('real_id_card')
    # 校验数据
    if not all([real_name, real_id_card]):
        return parameter_error()
    # 判断该用户是否已经实名认证过
    if g.user.real_name and g.user.real_id_card:
        return jsonify(errno=RET.DATAEXIST, errmsg='该用户已实名认证过')
    # 判断该真实姓名或身份证号是否被认证过
    try:
        users = Users.query.filter(or_(Users.real_name == real_name, Users.real_id_card == real_id_card)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户异常')
    if users:
        return jsonify(errno=RET.DATAEXIST, errmsg='该实名用户或身份证号已存在')
    # 进行实名认证, 保存实名信息
    g.user.real_name = real_name
    g.user.real_id_card = real_id_card
    try:
        db.session.add(g.user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户实名信息异常')

    return jsonify(errno=RET.OK)
