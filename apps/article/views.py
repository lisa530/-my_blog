from flask import Blueprint, request, g, redirect, url_for, render_template, jsonify, session

from apps.article.models import Article, Article_type, Comment
from apps.user.models import User
from exts import db

article_bp1 = Blueprint('article', __name__, url_prefix='/article')


# 自定义过滤器

@article_bp1.app_template_filter('cdecode')
def content_decode(content):
    content = content.decode('utf-8')
    return content



@article_bp1.route('/publish', methods=['POST', 'GET'])
def publish_article():
    """发表文章"""
    # post请求
    if request.method == 'POST':
        # 接收表单参数,文章标题,类型，内容
        title = request.form.get('title')
        type_id = request.form.get('type')
        content = request.form.get('content')
        # 添加文章
        article = Article()
        article.title = title
        article.type_id = type_id # 给关联字段赋值(文章所属性类型)
        article.content = content # 给关联字段赋值(文章内容)
        article.user_id = g.user.id # 当前登录用户
        db.session.add(article)
        db.session.commit()

        # 重定向到首页
        return redirect(url_for('user.index'))


@article_bp1.route('/detail')
def article_detail():
    """文章详情"""
    # 获取文章对象通过id
    article_id = request.args.get('aid')
    article = Article.query.get(article_id)
    # 获取文章分类
    types = Article_type.query.all()
    user = None
    # 从session中获取登录用户的uid
    user_id = session.get('uid', None)
    if user_id: # 用户已登录，查询数据库
        user = User.query.get(user_id)
    # 接收分页参数，默认为第1页
    page = int(request.args.get('page', 1))
    # 查询文章评论，查询条件：根据文章id查询，并且 按照文章评论时间最新排序，并且进行分页处理
    comments = Comment.query.filter(Comment.article_id == article_id) \
        .order_by(-Comment.cdatetime) \
        .paginate(page=page, per_page=5)

    # 渲染模板
    return render_template('article/detail.html', article=article, types=types, user=user, comments=comments)


@article_bp1.route('/love')
def article_love():
    """点赞"""
    # 1.根据文章id查询文章
    article_id = request.args.get('aid')
    # 从路径中取出tag参数
    tag = request.args.get('tag')
    # 查询文章
    article = Article.query.get(article_id)
    if tag == '1': # 表示已经点赞过
        article.love_num -= 1
    else:
        article.love_num += 1 # 对love_num属性进行加1操作
    db.session.commit()
    # 返回json数据
    return jsonify(num=article.love_num)


# 发表文章评论
@article_bp1.route('/add_comment', methods=['GET', 'POST'])
def article_comment():
    if request.method == 'POST':
        comment_content = request.form.get('comment')
        user_id = g.user.id
        article_id = request.form.get('aid')
        # 评论模型
        comment = Comment()
        comment.comment = comment_content
        comment.user_id = user_id
        comment.article_id = article_id
        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('article.article_detail') + "?aid=" + article_id)
    return redirect(url_for('user.index'))
