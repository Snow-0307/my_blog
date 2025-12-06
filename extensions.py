# extensions.py
"""
集中管理所有Flask扩展
避免循环导入，所有其他模块从这里导入扩展对象
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 创建扩展对象（先不绑定app）
db = SQLAlchemy()
migrate = Migrate()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    migrate.init_app(app, db)