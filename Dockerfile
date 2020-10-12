FROM python:3.7
MAINTAINER alex<g1242556827@163.com>
WORKDIR /Project/FlaskIhome

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
EXPOSE 5000

COPY . .

CMD ["gunicorn", "manager:app", "-c", "./gunicorn.conf.py"]