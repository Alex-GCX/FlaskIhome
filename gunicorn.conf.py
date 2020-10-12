# 定义同时开启的处理请求的进程数量，根据网站流量适当调整
workers = 2
# 采用gevent库，支持异步处理请求，提高吞吐量
worker_class = "gevent"
# 绑定IP和端口
bind = "0.0.0.0:5000"
# 使用后台守护进程的模式启动
# daemon = "true"

# 日志设置
# 设置gunicorn访问日志格式，错误日志无法设置
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# 访问日志的存储文件, 当前路径的logs目录下
accesslog = "logs/gunicorn_access.log"
# 错误日志的存储文件, 当前路径的logs目录下
errorlog = "logs/gunicorn_error.log"
# 日志记录等级
loglevel = 'info'
