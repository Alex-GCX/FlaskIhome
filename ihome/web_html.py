from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint('web_html', __name__)


@html.route('/<re(r".*"):html_file>')  # 使用自定的路由转换器re
def get_html(html_file):
    """根据url中的html_file返回static路径下的html文件"""
    # 若/后面为空, 则默认返回主页index.html
    if not html_file:
        html_file = 'index.html'
    # 若不是以html结尾, 则默认加上.html结尾
    if not html_file.endswith('.html'):
        html_file = html_file + '.html'
    # html文件在static下的html路径下, 而flask的静态路径只到static这一层, 因此需要在路径上拼上'html/'
    if html_file != 'favicon.ico':
        html_file = 'html/' + html_file

    # 生成response对象
    response = make_response(current_app.send_static_file(html_file))  # send_static_file能够将文件发送给浏览器
    # 生成csrf_token
    csrf_token = csrf.generate_csrf()
    # 设置cookie
    response.set_cookie('csrf_token', csrf_token)

    return response
