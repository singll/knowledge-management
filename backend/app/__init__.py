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
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()

                if not existing_tables:
                    logger.info("数据库为空，创建表...")
                    db.create_all()
                else:
                    logger.info(f"已有 {len(existing_tables)} 个表: {existing_tables}")
                    # 检查并添加新字段
                    migrate_webhook_tables(inspector)

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
            # 不要抛出异常，让应用继续运行


def migrate_webhook_tables(inspector):
    """迁移 webhook 相关表，添加新字段"""
    try:
        from sqlalchemy import text

        # 检查 webhook_configs 表的字段
        if 'webhook_configs' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('webhook_configs')]
            logger.info(f"webhook_configs 现有字段: {columns}")

            # 需要添加的新字段
            new_columns = {
                'content_type': "ALTER TABLE webhook_configs ADD COLUMN content_type VARCHAR(100) DEFAULT 'application/json'",
                'headers': "ALTER TABLE webhook_configs ADD COLUMN headers TEXT",
                'body_template': "ALTER TABLE webhook_configs ADD COLUMN body_template TEXT",
                'timeout': "ALTER TABLE webhook_configs ADD COLUMN timeout INTEGER DEFAULT 30"
            }

            for col_name, sql in new_columns.items():
                if col_name not in columns:
                    logger.info(f"添加 webhook_configs.{col_name} 字段...")
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                        logger.info(f"字段 {col_name} 添加成功")
                    except Exception as e:
                        db.session.rollback()
                        logger.warning(f"添加字段 {col_name} 失败: {e}")

        # 检查 webhook_history 表的字段
        if 'webhook_history' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('webhook_history')]
            logger.info(f"webhook_history 现有字段: {columns}")

            # 需要添加的新字段
            new_columns = {
                'request_url': "ALTER TABLE webhook_history ADD COLUMN request_url VARCHAR(500)",
                'request_method': "ALTER TABLE webhook_history ADD COLUMN request_method VARCHAR(10)",
                'request_headers': "ALTER TABLE webhook_history ADD COLUMN request_headers TEXT",
                'response_headers': "ALTER TABLE webhook_history ADD COLUMN response_headers TEXT",
                'duration': "ALTER TABLE webhook_history ADD COLUMN duration INTEGER"
            }

            for col_name, sql in new_columns.items():
                if col_name not in columns:
                    logger.info(f"添加 webhook_history.{col_name} 字段...")
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                        logger.info(f"字段 {col_name} 添加成功")
                    except Exception as e:
                        db.session.rollback()
                        logger.warning(f"添加字段 {col_name} 失败: {e}")

            # 修改 article_url 字段为可空（如果需要）
            # SQLite 不支持直接修改列约束，所以跳过这个操作

    except Exception as e:
        logger.error(f"Webhook 表迁移失败: {e}", exc_info=True)
