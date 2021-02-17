from flask import Blueprint, request, render_template

from article.models import Article
from ext import db
from user.models import User

article_bp = Blueprint('article', __name__)


@article_bp.route('/publish',methods=['GET','POST'])
def publish_article():
    """发布文章"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        uid = request.form.get('uid')
        # 添加文章
        article = Article()
        # 给对象的属性赋值
        article.title = title
        article.content = content
        article.user_id = uid
        # 添加到数据库
        db.session.add(article)
        db.session.commit()
        return '添加成功！'
    else:
        users = User.query.filter(User.isdelete == False).all()
        return render_template('article/add_article.html', users=users)


@article_bp.route('/show_article')
def show_article():
    """查询所有文章"""
    articles = Article.query.all()
    return render_template('article/show_article.html', articles=articles)


@article_bp.route('/select_article_user')
def select_article_user():
    """查询文章对应的用户"""
    id = request.args.get('id')
    user = User.query.get(id)
    return render_template('article/select_article_user.html', user=user)