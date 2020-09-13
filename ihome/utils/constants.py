from .commons import get_internet_host

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
SORTED_BY = ['new', 'booking', 'price-inc', 'price-des']

# 查询列表页每页数据量
SEARCH_HOUSES_PAGE_COUNT = 3

# 房屋查询结果缓存, 七天， 单位秒
SEARCH_HOUSES_EXPIRES = 7 * 24 * 3600

# 订单状态与显示关系
ORDER_STATUS = {
    'WAIT_ACCEPT': '待接单',
    'WAIT_PAYMENT': '待支付',
    'WAIT_COMMENT': '待评价',
    'COMPLETED': '已完成',
    'CANCELLED': '已取消',
    'REJECTED': '已拒绝',
}

# 支付宝支付设置-沙箱环境
# 支付宝网
ALIPAY_SERVER_URL = 'https://openapi.alipaydev.com/gateway.do'
# 应用ID
ALIPAY_APP_ID = '2016102200739747'
# 应用私钥
ALIPAY_PRIVATE_KEY = 'MIIEpAIBAAKCAQEAp3go2jC9b4o3+flwKtN7tnjCikipB+CbpeYcGraM8NKTfc8jP7nwzvFBJYiElm4usQ3Sh7QqDDDNPG3QuF6MHeVYBuT9ZZP9vzdPRs7R/VVRSLUCLWyZ87dMknLilkrVih9rfrwpGH35nkJO7c2zHvmNHaefOOO+Zxgv2ZCSt+ZDkuzFouZAZFEVpB/0UxlQsTKeQggqpIa6rrwCEaFwvaLl8Mboz2ErqzXdA1g29RTNB7bqTt7IfIFMgH+G1Z7tQOw+rhpmBwojs2jl/xJ8+Ai7ktBSToFqpHK3ROnYKc650vu+fLIUoXETzo9o3i15YdWCWipVEg9lpakLbdmLawIDAQABAoIBAAtMukTuoPmTs+8z+3OITYKkZ0v5Vx5m81mgSykqRBxDuRv2DATSwQLVmHW13mxgBtp/ekMZzvR/nnmDV1/5US77OJNOhCKEd8ydKMY4UkbrqM5lGD6EY2bkaVBAXDWT2xC0ygYFICi850jcZIL7LCjc4b6sfrvR8hj2stPVQ3ERBjgIPvGelgDpgGbISwozTaNJL9EpGuxSE+h8bgO3KunBM60XzaFyJoiY3afyzu+s4Gi51H6Auhkvi7quUjwyFFgYGV51nhadbNPC9SIPDOxpQaDah5Igz2PykTHLz4VDXt0PS2QU7uQQQskgnmr1KsNtR3b7icIrM5yGtg5d1lECgYEA6uhwrRrSoDKqmQBoMwRlR6a3bGXtVhyKRS3o8n0pJEwtcuwJ+OLmF32KlacZhVUjSHEsSn9w3vDXWOqpmLDs8HNDXPuPeUj64udDctVEs4neGiJ21MoOl3L3bd4ASiaAip8cx1MkG1iJ9+5aMqPWczbtns0fBomTpO6Z2J1+WAUCgYEAtoGV+Z/0ngXpkOKqGlE7DLZCDI6XaOJ4zGzGLgXe2PPTYjZwl9rk6ECxSO8mGKUqIbsdmaeHWaFWEgYHM5WRMG7sEV5PYTVYk78TOEkrv0W/S8B2pLr2CXPUJK1d9TsP4oc6D9xOsvIdA/GcK7dLsX6dnocyZiuRiHWfURZL4K8CgYEA5kqT1BC8tpKVTsPoY0OG6vSVU66lO0tlfqagfcGYKN6Jm+WtbRM8UYEg8M/NpDowCd/xdON1Swq/g4siUu/4iU3ml2yDXnregr4IELbl0EFzvRlWeAvSvETYLxx6Gjeewsd0FjD679ggAjDoukaGgZMy5wDezrDnTsUfjA3yg+UCgYAhKq+cq8sCpMRrhiWvnq+CgeTC727oqq+VRvdFCeATwUva/1W64xbSdl9Bh+R+ehWMB7s7X0yjp0RDBkFsyHOYP7A6/86hNdahEwplIjcHDZ/UHmfxS+DGmvwkpjT7Cf67BiQxGbJbptBLFS9yal8hJId0ddFc6/IIwIdxbwHfFQKBgQDJFx7UEExZRoSuzG1n9YV2TcPwUdXmih5pA9gjNr75+1zEDtzIVTyvJz0bw10hwJxUt/LsQHasOobTAZicHAzdKjDXf/dDfAvgm8YcpM1YoWHqRTPUEiI3cvYd5hii+D1Ney0ShFTD5Svq9sJtBf2H+GJmZM4IbEEZryVqNeaQeQ=='
# 支付宝公
ALIPAY_PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu7VpkMSjW6ay396lyF6LA4piwaTyJsPaedCt4Vd5gNgQP9sZA/4kZ56jh3F8a8D7/mPvzU/l8ZWQSDdh5WoF6mweGdvLLKJefdM7FY3knpxw/wZKHFJAvLbP1Myy1d7ifnkH0vy0+WyWO5bBqm1yaqIJizlBsHhMBemS5kdvApNA6nLeMANxda8wsS2O39fNTfyHNysivybbHo+jzmTZLKQHQDxyz1S9AZ0bAl/NnZxj73vgQzvqfYlWZdflxByTrjqMlAo74UGNbghsWd8vLvK75kkL3h3r6b7/KPFSJ2uAZpnFgfKk/2m5DXMD3yzLMMl+0mQFRDr3Kti3PVqddQIDAQAB'
# 订单超时时间：如果买家超过这个时间不付款,会关闭交易(最小1m分钟)
ALIPAY_EXPRESS = '10m'
# 产品码
PRODUCT_CODE = 'QUICK_WAP_WAY'
# 回调通知地址
# 获取当前运行环境的公网IP地址
internet_host = get_internet_host()
# 支付宝返回的url, 给跳转给用户访问
ALIPAY_RETURN_URL = f"http://{internet_host}:5000/payresult.html"
# 支付宝后台访问的url, 用户无感
ALIPAY_NOTIFY_URL = ""
# 买家账号
# wreivn1390@sandbox.com
# 111111DXMD3yzLMMl+0mQFRDr3Kti3PVqddQIDAQAB'
