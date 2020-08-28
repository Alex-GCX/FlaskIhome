# 图片验证码的redis有效期, 单位：秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔, 单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 一个用户一分钟内只能登录5次
USER_LOGIN_EXPIRES = 60
USER_LOGIN_COUNT = 5

# 容联云短信设置
ACCID = '8aaf07087249953401727fa88e1e1c9d'
ACCTOKEN = '653e8d1fe37d40b589ad85948fefc3ce'
APPID = '8aaf07087249953401727fa88f011ca4'

# 七牛云图片存储设置
QN_ACCESS_KEY = 'kF97AuR8DoXn6XAlKQxYu7r5vdq9a1OYP37YRJ5Z'
QN_SECRET_KEY = 'sSSxlD9fpUxyRH8TBK21G_Ic67ydoBe-OYgjcjyM'
QN_BUCKET_NAME = 'alex-ihome'
QN_HOST = 'http://qfan653gi.hd-bkt.clouddn.com/'

# 城区缓存信息, 七天， 单位秒
AREA_REDIS_EXPIRES = 7 * 24 * 3600

# 评论展示条数
COMMENT_DISPLAY_COUNTS = 10

# 房屋详情缓存信息, 七天， 单位秒
HOUSE_REDIS_EXPIRES = 7 * 24 * 3600

# 首页最多展示房屋数量
INDEX_HOUSES_COUNT = 5

# 首页房屋缓存信息, 七天， 单位秒
INDEX_HOUSES_EXPIRES = 7 * 24 * 3600

# 查询排序范围
SORTED_BY = ['latest', 'hot', 'price', '-price']

# 房屋查询结果缓存, 七天， 单位秒
SEARCH_HOUSES_EXPIRES = 7 * 24 * 3600
