from ihome import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class BasicModel(db.Model):
    """建表的基类"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.Datetime, nullable=False, default=datetime.now())
    updated_date = db.Column(db.Datetime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_delete = db.Column(db.Boolean, nullable=False, default=False)


class Users(BasicModel):
    """用户模型类"""
    __tablename__ = 'ih_users'

    phone = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(240), unique=True, nullable=False)
    image_url = db.Column(db.String(240))
    real_name = db.Column(db.String(30), unique=True)
    real_id_card = db.Column(db.Integer, unique=True)

    # 将密码password设置为方法属性, 该属性不能读取, 只能赋值
    @property
    def password(self):
        raise AttributeError('密码不允许被读取')

    #  Users.password='xxxx'赋值密码时, 将输入的密码加密后存入数据库中
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 校验用户登录时输入的密码
    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)


class Areas(BasicModel):
    """城区模型类"""
    __tablename__ = 'ih_areas'

    name = db.Column(db.String(32), unique=True, nullable=False)


class Houses(BasicModel):
    """房屋模型类"""
    __tablename__ = 'ih_houses'

    user_id = db.Column(db.Integer, db.ForeignKey('ih_users.id'), nullable=False)
    user = db.relationship('Users', backref='houses')
    area_id = db.Column(db.Integer, db.ForeignKey('ih_areas.id'), nullable=False)
    area = db.relationship('Areas', backref='houses')

    title = db.Column(db.String(240), nullable=False)
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    address = db.Column(db.String(512))  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32))  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64))  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 该房屋的历史订单数
    default_image_url = db.Column(db.String(240))  # 默认显示的图片


class HouseImages(BasicModel):
    """房屋图片表"""
    __tablename__ = 'ih_house_images'

    house_id = db.Column(db.Integer, db.ForeignKey('ih_houses.id'), nullable=False)
    house = db.relationship('Houses', backref='images')
    image_url = db.Column(db.String(240), nullable=False)


house_facilities = db.Table('ih_house_facilities',
                            db.Column('house_id', db.Integer, db.ForeignKey('ih_houses.id'), nullable=False),
                            db.Column('facility_id', db.Integer, db.ForeignKey('ih_facilities.id'), nullable=False))


class Facilities(BasicModel):
    """基础设置模型类"""
    __tablename__ = 'ih_facilities'

    name = db.Column(db.String(32), nullable=False)


class Orders(BasicModel):
    """订单模型类"""
    __tablename__ = 'ih_orders'

    user_id = db.Column(db.Integer, db.ForeignKey('ih_orders.id'), nullable=False)
    user = db.relationship('Users', backref='orders')
    house_id = db.Column(db.Integer, db.ForeignKey('ih_houses.id'), nullable=False)
    house = db.relationship('House', backref='orders')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.Enum('NEW', 'PAID', 'ACCEPTED', 'COMPLETED', 'REJECTED', 'CANCELLED'), default='NEW', index=True)
