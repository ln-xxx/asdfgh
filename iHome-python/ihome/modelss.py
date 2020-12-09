from datetime import datetime
from . import db
from ihome import constants
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel(object):
    #公用类
    create_time = db.Column(db.DateTime,detalt = datetime.now)
    updata_time = db.Column(db.DateTime,default= datetime.now,onupdate=datetime.now)

class user(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32),unique=True,nullable=False)
    password_hash = db.Column(db.String(128),nullable=True)
    mobile = db.Column(db.Integer,unique=True,nullable=False)
    real_name = db.Column(db.String(10))
    id_real = db.Column(db.String(20))
    avatar_url = db.Column(db.String(123))
    houses = db.relationship('House',backref='user')
    orders = db.relationship('Order',backref = 'user')



    @property
    def password(self):
        raise AttributeError('不可读')


    @password.setter
    def paswword(self,passwd):
        self.password_hash = generate_password_hash(passwd)

    def check_password(self,passwd):
        return check_password_hash(self.password_hash,passwd)

    def to_dict(self):
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar": constants.QINIU_URL_DOMAIN + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:S")


        }
        return user_dict

    def auto_to_dict(self):

        auto_dict = {
            "user_id": self.id,
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return auto_dict


class Area(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name =  db.Column(db.String(32))
    houses = db.relationship('House',backref = 'area')

    def to_dict(self):
        area_dict = {
            "aid": self.id,
            "aname": self.name
        }
        return area_dict
