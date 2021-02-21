from datetime import datetime

from exts import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100))
    isdelete = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    # 增加一个字段
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='user')

    def __str__(self):
        return self.username


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_name = db.Column(db.String(50), nullable=False)
    photo_datetime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return self.photo_name


class AboutMe(db.Model):
    """关于我"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.BLOB, nullable=False)
    pdatetime = db.Column(db.DateTime, default=datetime.now)
    # 要与用户建立联系
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref='about')


class MessageBoard(db.Model):
    """留言表"""
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    mdatetime = db.Column(db.DateTime,default=datetime.now,doc='创建时间')
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),doc='关联用户的主键')
    # 添加关联查询字段,backref：表示在User表中添加一个字段messages
    # 主表查询子表：user.messages(查询用户对应的留言信息)
    # 子表查询主表：messageboard.user(查询留言对应用户是谁)
    user = db.relationship('User',backref='messages',doc='添加关联查询字段')