from flask import Blueprint, request, g, redirect, url_for, render_template, jsonify

from apps.article.models import Article, Article_type
from exts import db

article_bp1 = Blueprint('article', __name__, url_prefix='/article')


# 自定义模板过滤器
@article_bp1.app_template_filter('cdeocde')
def content_decode(content):
    """实现文章内容解码"""
    content = content.decode('utf-8')
    return content


@article_bp1.route('/publish', methods=['POST', 'GET'])
def publish_article():
    """发布文章"""
    if request.method == 'POST':
        # 接收表单参数
        title = request.form.get('title')
        type_id = request.form.get('type')
        content = request.form.get('content')
        # 添加文章
        article = Article()
        article.title = title
        article.type_id = type_id
        article.content = content
        article.user_id = g.user.id
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('user.index'))


@article_bp1.route('/detail')
def article_detail():
    """文章详情"""
    # 接收文章id
    article_id = request.args.get('aid')
    # 根据文章id查询数据库
    article = Article.query.get(article_id)
    # 查看所有的文章类型
    types = Article_type.query.all()
    # 渲染文章详情信息
    return render_template('article/detail.html', article=article, types=types)


@article_bp1.route('/love')
def article_love():
    """文章电宰点赞"""
    # 获取查询参数 文章id
    article_id = request.args.get('aid')
    tag = request.args.get('tag') # 标记,用户是否点赞
    # 根据文章对象
    article = Article.query.get(article_id)
    # 判断是否点赞
    if tag == '1': # 已点赞
        article.love_num -= 1 # 将love_num属性值减1
    else:
        article.love_num += 1
    db.session.commit()
    # 返回json数据
    return jsonify(num=article.love_num)
