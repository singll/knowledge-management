"""Flask 应用工厂"""
import logging
import os
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db
from app.api import register_blueprints

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """创建 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 初始化数据库
    init_database(app)
    
    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'version': '1.0.0'}
    
    return app


def init_database(app):
    """初始化数据库"""
    with app.app_context():
        try:
            # 导入所有模型
            from app import models  # noqa: F401
            
            # 检查数据库文件是否存在
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            db_exists = os.path.exists(db_path)
            
            if not db_exists:
                logger.info("首次启动，创建数据库表...")
                db.create_all()
                logger.info("数据库表创建完成")
            else:
                logger.info("数据库已存在，跳过创建")
                # 使用 inspector 检查表是否完整
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                if not existing_tables:
                    logger.info("数据库为空，创建表...")
                    db.create_all()
                else:
                    logger.info(f"已有 {len(existing_tables)} 个表: {existing_tables}")
                    
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
            # 不要抛出异常，让应用继续运行
