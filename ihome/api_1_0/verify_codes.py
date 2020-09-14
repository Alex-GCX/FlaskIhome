from flask import make_response, jsonify, current_app, request
from ihome.utils.captcha import captcha
from ihome.utils import constants
from ihome.utils.response_codes import RET
from ihome import redis_connect
from ihome.models import Users
from . import api
import random


@api.route('/image_codes/<image_code_key>')
def get_image_code(image_code_key):
    # 获取验证码
    name, text, image_data = captcha.generate_captcha()
    print(f'真实图片验证码：{text}')
    # 保存验证码
    try:
        redis_connect.setex(image_code_key, constants.IMAGE_CODE_REDIS_EXPIRES,
                            text)  # setex(key, 过期时间, value)=set+expire
    except Exception as e:
        # 保存失败, 记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    # 保存成功
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


@api.route("/sms_codes/<re(r'1[^120]\d{9}'):phone>")
def send_sms_code(phone):
    # 获取url中？参数
    image_code = request.args.get('image_code')
    image_code_key = request.args.get('image_code_key')
    # 判断参数是否有值
    if not all([image_code, image_code_key]):
        return jsonify(errno=RET.PARAMERR, errmsg='图片验证码参数不能为空')

    # 判断该手机号是否已经注册过
    try:
        user = Users.query.filter_by(phone=phone).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户异常')
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已注册过用户')

    # 判断该手机号一分钟内是否发送过短信
    try:
        his_sms_code_key = f'his_sms_code_{phone}'
        sms_his = redis_connect.get(his_sms_code_key)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis获取短信验证码异常')
    # 存在短信记录
    if sms_his:
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号一分钟内已发送过短信，请稍候再试')

    # 获取redis中的真实图片验证码
    try:
        real_image_code = redis_connect.get(image_code_key)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='读取图片验证码异常')
    # 判断验证码是否存在
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已失效')
    # 删除redis中的图片验证码，防止同一个验证码被使用多次
    try:
        redis_connect.delete(image_code_key)
    except Exception as e:
        current_app.logger.error(e)
    # 比较用户输入的验证码与真实验证码
    if image_code.lower() != real_image_code.decode().lower():
        # 验证码错误
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 图片验证码正确，则发送短信验证码
    # 获取随机6位验证码
    # sms_code = '%06d' % random.randint(0, 999999)
    sms_code = f'{random.randint(0, 999999):06}'
    print(f'真实短信验证码：{sms_code}')
    # try:
    #     sdk = SmsSDK(constants.ACCID, constants.ACCTOKEN, constants.APPID)
    #     tid = '1'
    #     mobile = phone
    #     # 短信模板为：....您的验证码是{1}，请于{2}分钟内正确输入
    #     # data参数为元组，第一个值为模板中的{1}，第二个值为模板中的{2}
    #     data = (sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60)
    #     # 发送短信，接受返回值
    #     sms_resp_json = sdk.sendMessage(tid, mobile, data)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # # 处理返回值
    # sms_resp_dict = json.loads(sms_resp_json)
    # sms_status = sms_resp_dict.get('statusCode')
    # if sms_status not in ('000000', '112310'):
    #     # 发送失败
    #     return jsonify(errno=RET.THIRDERR, errmsg=sms_resp_dict.get('statusMsg'))
    # 异步发送短信
    from ihome.celery_tasks.send_sms_code import tasks
    result = tasks.send_sms_code.delay(sms_code, phone)

    # 发送成功
    # redis缓存发送记录，一分钟内同一个手机号不能再发送短信了
    try:
        redis_connect.setex(his_sms_code_key, constants.SEND_SMS_CODE_INTERVAL, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis保存短信验证码记录异常')

    # 保存短信验证码
    try:
        sms_code_key = f'sms_code_{phone}'
        redis_connect.setex(sms_code_key, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_connect.setex(sms_code_key, 432000, sms_code)  # 暂时存5天
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis保存短信验证码异常')

    return jsonify(errno=RET.OK)
