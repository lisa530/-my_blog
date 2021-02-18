from datetime import datetime
from ext import db


class Article_type(db.Model):
    """文章分类表(一类)"""

    __tablename__ = 'type' # 指定表名
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    type_name = db.Column(db.String(20),nullable=False,doc='文章分类名称')
    # 添加一个关系查询字段
    # 多查一:查询文章类型下的文章,通过article_type.articles
    # 一查多:查询文章属于哪个分类,article.article_type
    articles = db.relationship('Article',backref='article_type')


class Article(db.Model):
    """文章表(子表)"""
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,doc='主键')
    title = db.Column(db.String(50),nullable=False,doc='标题')
    content = db.Column(db.Text,nullable=False,doc='文章内容')
    pubdatetime = db.Column(db.DateTime,default=datetime.now,doc='发布时间')
    click_num = db.Column(db.Integer,default=0,doc='点赞')
    save_num = db.Column(db.Integer,default=0,doc='收藏')
    love_num = db.Column(db.Integer,default=0,doc='喜欢')
    # 外键:一个用户对应多篇文章
    # 注意:外键只能写在多类中
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    # 外键:一篇文章对应多个分类
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    # 添加关联查询字段，查询文章对应的评论，article.comments, 查询评论属于哪篇文章：comment.article
    comments = db.relationship('Comment',backref='article')

    def __str__(self):
        return self.title


class Comment(db.Model):
    """文章和文章类型的关系表"""
    __tablename__ = 'comment'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    comment = db.Column(db.String(255),nullable=False,doc='评论')
    # 外键:评论属于哪个用户
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),doc='关联用户的主键')
    # 外键:评论属于哪篇文章
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'),doc='关联文章的主键')
    cdatetime = db.Column(db.DateTime,default=datetime.now(),doc='创建时间')

    def __str__(self):
        return self.comment

