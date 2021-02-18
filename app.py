from ext import db
# 导入工厂函数
from apps import create_app
# 导入迁移框架
from flask_migrate import MigrateCommand,Migrate
# 导入flask脚本管理模块
from flask_script import Manager

# from apps.goods.models import *
# from apps.article.models import *
# from apps.user.models import User

# 实例化create_app
app = create_app()
# 实例化Manage对象
manage = Manager(app)
# 实例化迁移框架
migrate = Migrate(app,db)
# 添加命令到manage对象中
manage.add_command('db',MigrateCommand)


if __name__ == '__main__':
    # app.run()
    print(app.url_map)
    manage.run()
