from flask_migrate import Migrate, MigrateCommand # 数据库迁移模块
from flask_script import Manager # flask扩展启动脚本模块
from apps.user.models import *
from apps.article.models import *
from apps import create_app
from exts import db # 数据库对象

# 实例化工厂函数
app = create_app()
# 实例化脚本管理对象
manager = Manager(app=app)
# 实例化数据迁移框架,将flask的app对象和数据库db对象绑定到对象上
migrate = Migrate(app=app, db=db)
# 添加命令到脚本管理对象
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # 使用脚本启动
    manager.run()
