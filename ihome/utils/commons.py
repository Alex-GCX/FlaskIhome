from werkzeug.routing import BaseConverter
from flask import session, jsonify, g, current_app
from .response_codes import RET
from ihome.models import Users
import functools
import json
import requests


class ReConverter(BaseConverter):
    """自定义路由转换器"""

    def __init__(self, url_map, regex):
        # 调用父类的__init__方法
        super().__init__(url_map)
        # 将正则表达式参数保存到regex属性中
        self.regex = regex


def login_required(view_func):
    """登录验证装饰器"""

    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断登录状态
        user_id = session.get('user_id')

        if not user_id:
            # 没有登录
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

        # 已登录，将user保存在g对象中
        try:
            user = Users.query.get(user_id)
            g.user = user
            print(g.user)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取用户异常')
        # 执行视图函数
        return view_func(*args, **kwargs)

    return wrapper


def parameter_error():
    return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')


def get_internet_host():
    # 访问 https://jsonip.com/ 获取json结果
    response = requests.get('https://jsonip.com/').text
    # json 转为字典
    response = json.loads(response)
    # 字典提取ip
    return response['ip']
