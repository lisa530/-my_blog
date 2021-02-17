from flask import Flask
from ext import db # 导入数据库db对象
from settings import DevelopmentConfig
# 用户蓝图
from apps.user.views import user_bp

# 文章蓝图
from apps.article.views import article_bp
from ext import bookstrap


def create_app():
    """封装工厂函数"""
    app = Flask(__name__,template_folder='../templates',static_folder='../static')
    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(article_bp)

    # 初始化db对象
    db.init_app(app)
    # 初始化bootstrap
    bookstrap.init_app(app)
    # 加载配置信息
    app.config.from_object(DevelopmentConfig)
    # 返回app
    return app


