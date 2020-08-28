from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ihome import db
from ihome.utils.constants import COMMENT_DISPLAY_COUNTS


class BasicModel(db.Model):
    """建表的基类"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
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

    # 友好展示模型类对象
    def __repr__(self):
        return self.name


class Areas(BasicModel):
    """城区模型类"""
    __tablename__ = 'ih_areas'

    name = db.Column(db.String(32), unique=True, nullable=False)

    # 友好展示模型类对象
    def __repr__(self):
        return self.name


# 房屋和设置表属于多对多关系, 官方推荐db.table的方式建立多对多关系
house_facilities = db.Table('ih_house_facilities',
                            db.Column('house_id', db.Integer, db.ForeignKey('ih_houses.id'), nullable=False),
                            db.Column('facility_id', db.Integer, db.ForeignKey('ih_facilities.id'), nullable=False))


class Houses(BasicModel):
    """房屋模型类"""
    __tablename__ = 'ih_houses'

    user_id = db.Column(db.Integer, db.ForeignKey('ih_users.id'), nullable=False)
    user = db.relationship('Users', backref='houses')
    area_id = db.Column(db.Integer, db.ForeignKey('ih_areas.id'), nullable=False)
    area = db.relationship('Areas', backref='houses')

    title = db.Column(db.String(240), nullable=False)
    price = db.Column(db.Integer, default=0)  # 单价，单位：元
    address = db.Column(db.String(512))  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32))  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64))  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，负数表示不限制
    order_count = db.Column(db.Integer, default=0)  # 该房屋的历史订单数
    default_image_url = db.Column(db.String(240))  # 默认显示的图片
    facilities = db.relationship('Facilities', secondary=house_facilities, backref='houses')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'title', name='uix_ih_houses_user_id_title'),
    )

    # 友好展示模型类对象
    def __repr__(self):
        return self.title

    # 房屋列表页的信息
    def get_list_info(self):
        return {
            'house_id': self.id,
            'title': self.title,
            'area_name': self.area.name,
            'price': self.price,
            'created_date': datetime.strftime(self.created_date, '%Y-%m-%d %H:%M:%S'),
            'img_url': self.default_image_url,
        }

    # 房屋详细信息
    def get_detail_info(self):
        return {
            'img_urls': [image.image_url for image in self.images],
            'title': self.title,
            'price': self.price,
            'owner_id': self.user.id,
            'owner_img_url': self.user.image_url,
            'owner_name': self.user.name,
            'address': self.address,
            'room_count': self.room_count,
            'acreage': self.acreage,
            'unit': self.unit,
            'capacity': self.capacity,
            'beds': self.beds,
            'deposit': self.deposit,
            'min_days': self.min_days,
            'max_days': self.max_days,
            'facilities': [facility.id for facility in self.facilities],
            'comments': [order.get_comment() for order in self.get_comment_orders()],
        }

    # 房屋查询页信息
    def get_search_info(self):
        return {
            'house_id': self.id,
            'title': self.title,
            'img_url': self.default_image_url,
            'owner_img_url': self.user.image_url,
            'price': self.price,
            'room_count': self.room_count,
            'order_count': self.order_count,
            'address': self.address
        }

    def get_comment_orders(self):
        """获取房屋评论过的订单"""
        # 房屋ID当前房屋的/订单状态为已完成的/评论内容不为空的/根据最后更新时间倒叙排序/获取前10条评论展示
        orders = Orders.query.filter(Orders.house_id == self.id, Orders.status == 'COMPLETED',
                                     Orders.comment is not None).order_by(Orders.updated_date.desc()).limit(
            COMMENT_DISPLAY_COUNTS).all()
        return orders


class HouseImages(BasicModel):
    """房屋图片表"""
    __tablename__ = 'ih_house_images'

    house_id = db.Column(db.Integer, db.ForeignKey('ih_houses.id'), nullable=False)
    house = db.relationship('Houses', backref='images')
    image_url = db.Column(db.String(240), nullable=False)


class Facilities(BasicModel):
    """基础设置模型类"""
    __tablename__ = 'ih_facilities'

    name = db.Column(db.String(32), nullable=False)

    # houses = db.relationship('Houses', sencondary=house_facilities, backref='facilities')

    # 友好展示模型类对象
    def __repr__(self):
        return self.name


class Orders(BasicModel):
    """订单模型类"""
    __tablename__ = 'ih_orders'

    order_num = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ih_users.id'), nullable=False)
    user = db.relationship('Users', backref='orders')
    house_id = db.Column(db.Integer, db.ForeignKey('ih_houses.id'), nullable=False)
    house = db.relationship('Houses', backref='orders')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.Enum('NEW', 'PAID', 'ACCEPTED', 'COMPLETED', 'REJECTED', 'CANCELLED'), default='NEW',
                       index=True)

    # 友好展示模型类对象
    def __repr__(self):
        return self.order_num

    # 获取评论信息
    def get_comment(self):
        """获取评论信息"""
        return {
            'user_name': self.user.name if self.user.name != self.user.phone else '匿名用户',
            'comment_date': datetime.strftime(self.updated_date, '%Y-%m-%d %H:%M:%S'),
            'comment': self.comment
        }
