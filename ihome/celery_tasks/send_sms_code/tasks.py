from ihome.celery_tasks.main import celery
from ronglian_sms_sdk import SmsSDK
from ihome.utils import constants
from ihome.utils.response_codes import RET
from flask import current_app
import json


@celery.task
def send_sms_code(sms_code, phone):
    """发送短信任务"""
    result = {'errno': RET.OK}
    try:
        sdk = SmsSDK(constants.ACCID, constants.ACCTOKEN, constants.APPID)
        tid = '1'
        mobile = phone
        # 短信模板为：....您的验证码是{1}，请于{2}分钟内正确输入
        # data参数为元组，第一个值为模板中的{1}，第二个值为模板中的{2}
        data = (sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60)
        # 发送短信，接受返回值
        sms_resp_json = sdk.sendMessage(tid, mobile, data)
    except Exception as e:
        current_app.logger.error(e)
        result['errno'] = RET.THIRDERR
        result['errmsg'] = '发送短信异常'
    else:
        # 处理返回值
        sms_resp_dict = json.loads(sms_resp_json)
        sms_status = sms_resp_dict.get('statusCode')
        if sms_status not in ('000000', '112310'):
            # 发送失败
            result['errno'] = RET.THIRDERR
            result['errmsg'] = sms_resp_dict.get('statusMsg')
    return result
