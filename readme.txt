"""
一对多
常见的比如：班级对学生，部门对员工，学校对班级，用户对文章，用户对订单

	可以说一个班级有多名同学或者一个部门有多名员工，但是不能说：

	一个学生属于多个班级，一个员工属于多个部门，一个班级属于多个学校....
"""
	


"""在flask的框架中如何体现1对多的模型关系？"""

# 就是通过外键ForignKey和relationship体现。
# ForignKey表示关联两张表的关系，relationship是给模板使用的。


class User(db.Model):
	"""用户类(一类)"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100))
    isdelete = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    # 增加关联查询字段
    # relationship关联哪个模型类,backref，表示给关联的模型类添加一个user属性
    # 查询用户的文章：user.articles,查询文章对应的用户：articles.user 
    articles = db.relationship('Article', backref='user')
    
	
    def __str__(self):
        return self.username


"""
使用db.ForeignKey关联外键字段只能写在多类中
使用关联查询时，relationship可以定义在任意模型类中
"""

from datetime import datetime

from exts import db


class Article(db.Model):
	"""文章类(多的一方)"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pdatetime = db.Column(db.DateTime, default=datetime.now)
    click_num = db.Column(db.Integer, default=0)
    save_num = db.Column(db.Integer, default=0)
    love_num = db.Column(db.Integer, default=0)
    # 外键 同步到数据库的外键关系
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	


"""
多对多：
常见的多对多：
用户对文章评论，用户对商品，学生对课程

一个用户可以买多个商品，反过来这个商品的还可以让多个用户购买

一个学生可以选择多门课程，反过来一门课程还可以让多个学生选择

一个用户可以有多个评论，反过来一个评论可以有多个用户

一个用户可以发表多篇文章，反过来一篇文章可以有多个用户

#####多对多使用一张中间表记录两张表的外键字段####
"""


# 例如：用户和商品之间为多对多关系

class Goods(db.Model):
    """商品表"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gname = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # 反向引用，db.relationship表示关联的模型类，backref表示在User表中添加一个属性goodslist
    # 一查多：通过一类模型类.一类外键字段，根据商品找对应的用户:通过goods.users， 
    # 多查一：根据多类模型类.多类关系字段， 根据用户找对应的商品:通过 user.goodslist
    # secondary多对多关系中，根据哪个表(中间表)查找两张表之间的关系
    users = db.relationship('User', backref='goodslist', secondary='user_goods')

    def __str__(self):
        return self.gname
        



class User(db.Model):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100))
    isdelete = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    # 增加关系字段，用于一对多查询使用
    # db.relationship()第一个参数表示关联另一个模型类，第二个参数backref，向Article类中添加一个user属性
    # 多查一：通过acticles.user获取到文章对应的用户，一查多：通过user.atricles获取用户的文章信息
    articles = db.relationship('Article', backref='user')

    def __str__(self):
        return self.username
        
        

class User_goods(db.Model):
    """关系表，存放user和goods之间的关系"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键，关联用户表的主键id字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 外键，关联商品表的主键id字段
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    number = db.Column(db.Integer, default=1)
    
    
    
    

