from datetime import datetime

from ext import db


class User(db.Model):
    """用户类(一类)"""
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(11),unique=True,nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100),doc='图标')
    isdelete = db.Column(db.Boolean,default=False,doc='逻辑删除')
    credatetime = db.Column(db.DateTime,default=datetime.now,doc='创建时间')
    # 增加一个关联查询字段,relationship关联哪个模型类,backref 在Article表中添加一个属性user
    # 一查多:通过user.articles查询用户的文章
    # 多查一:通过article.user查询文章对应的用户
    articles = db.relationship('Article', backref='user')

    def __str__(self):
        return self.username