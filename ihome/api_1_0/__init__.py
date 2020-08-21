from flask import Blueprint

# 创建蓝图
api = Blueprint('api_1_0', __name__, url_prefix='/api/v1.0')

# 导入蓝图的视图
from . import users, verify_codes
