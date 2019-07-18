from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from SLife import constants
from flask_sqlalchemy import SQLAlchemy


# 数据库
db = SQLAlchemy()


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class User(BaseModel, db.Model):
    """用户信息"""
    __tablename__ = "sl_user_profile"

    id =db.Column(db.Integer, primary_key=True) # 用户编号
    name = db.Column(db.String(32), nullable=False) # 用户昵称
    avatar_url = db.Column(db.String(512)) # 头像二进制数据流
    gender = db.Column(db.Integer, default=1)  # 性别 0==保密，1==男，2==女
    province = db.Column(db.String(32), nullable=False) # 省份
    city= db.Column(db.String(32), nullable=False) # 城市
    signature = db.Column(db.String(128)) # 个性签名
    openid = db.Column(db.String(64), index=True) # 用户唯一标识符
    dynamics = db.relationship("Dynamic", backref="user") # 用户发布的动态

    def to_base_dict(self):
        if self.gender==1:
            a="男"
        elif self.gender==2:
            a="女"
        else:
            a="保密"

        User_dict = {
            "user_id": self.id,
            "user_name": self.name,
            "avatar_url": self.avatar_url,
            "gender": a,
            "province": self.province,
            "city": self.city,
            "signature": self.signature,
        }
        return User_dict


class Dynamic(BaseModel, db.Model):
    """动态"""
    __tablename__ = "sl_dynamic_info"

    id = db.Column(db.Integer, primary_key=True) # 动态编号
    user_id = db.Column(db.Integer, db.ForeignKey("sl_user_profile.id")) #动态发布者编号
    content = db.Column(db.String(256), nullable=False) # 动态内容
    content_image_url = db.Column(db.String(128)) # 用户头像路径
    goods = db.relationship("Good", backref="dynamic") # 用户点赞
    comments = db.relationship("Comment", backref="dynamic") # 用户评论

    def to_base_dict(self):
        dynamic_dict = {
            "dynamic_id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "content_imag_url": constants.QINIU_IMAGE_IP_NAME + self.content_image_url if self.content_image_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return dynamic_dict


class Good(BaseModel, db.Model):
    """点赞"""

    __tablename__ = "sl_good_info"

    id = db.Column(db.Integer, primary_key=True) # 点赞编号
    dynamic_id = db.Column(db.Integer, db.ForeignKey("sl_dynamic_info.id")) # 点赞的动态编号
    username = db.Column(db.String(32)) # 点赞人的名字
    user_id = db.Column(db.Integer) # 点赞人id
    status = db.Column(db.String(32), server_default="false")

    def to_base_dict(self):
        dict = {
            "status": self.status
        }
        return dict

class Comment(BaseModel, db.Model):
    """评论模型类"""

    __tablename__ = "sl_comment_info"

    id = db.Column(db.Integer, primary_key=True) # 评论编号
    dynamic_id = db.Column(db.Integer, db.ForeignKey("sl_dynamic_info.id")) # 评论的动态编号
    content = db.Column(db.String(1024)) # 评论内容
    from_user_id = db.Column(db.Integer) # 评论人id

    def to_base_dict(self):
        dict = {
            "content":self.content,
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return dict

# class replay(BaseModel, db.Model):
#     """回复"""
#     __tablename__ = "sl_replay_info"
#
#     id = db.Column(db.Integer, primary_key=True) # 回复编号
#     comment_id = db.Column(db.Integer, db.ForeignKey("sl_comment_info.id")) # 回复的评论id
#     replay_type = db.Column(db.String(64)) # 回复类型
#     content = db.Column(db.String(1024)) # 回复内容
#     from_user_id = db.Column(db.Integer) # 回复人的 id
#     """
#     目标用户id，
#     当replay_type为comment时, replay_id是 comment表中的from_user_id
#     当replay_type为replay时, replay_id是 replay表中的from_replay_id
#     """
#     to_user_id = db.Column(db.Integer) # 回复的人的 id













