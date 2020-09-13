workers = 5  # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
worker_class = "gevent"  # 采用gevent库，支持异步处理请求，提高吞吐量
bind = "0.0.0.0:5000"
daemon = "true"  # 后台进程
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'  # 设置gunicorn访问日志格式，错误日志无法设置
accesslog = "./logs/gunicorn_access.log"  # 访问日志文件
errorlog = "./logs/gunicorn_error.log"  # 错误日志文件
loglevel = 'info'
