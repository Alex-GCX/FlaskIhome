# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag
import qiniu.config
from .constants import QN_ACCESS_KEY, QN_SECRET_KEY, QN_BUCKET_NAME, QN_HOST


def storage(data):
    """七牛上传图片接口"""

    # 需要填写你的 Access Key 和 Secret Key
    access_key = QN_ACCESS_KEY
    secret_key = QN_SECRET_KEY
    # access_key = 'kF97AuR8DoXn6XAlKQxYu7r5vdq9a1OYP37YRJ5Z'
    # secret_key = 'sSSxlD9fpUxyRH8TBK21G_Ic67ydoBe-OYgjcjyM'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = QN_BUCKET_NAME
    # bucket_name = 'alex-ihome'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 上传二进制文件
    ret, info = put_data(token, None, data)
    # print('*'*10, 'ret', '*'*10)
    # print(ret)
    # print('*'*10, 'info', '*'*10)
    # print(info)
    url = QN_HOST + ret.get("key")
    return {'status': info.status_code, 'errmsg': info.exception, 'url': url}


if __name__ == '__main__':
    with open('ironman.jpg', 'rb') as f:
        data = f.read()
        storage(data)
