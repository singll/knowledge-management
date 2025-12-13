"""配置管理"""
import os
from pathlib import Path

class Config:
    """基础配置"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # 数据库
    BASE_DIR = Path(__file__).parent.parent
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "data" / "knowledge.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # RagFlow
    RAGFLOW_URL = os.getenv('RAGFLOW_URL', 'http://localhost:9380')
    RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY', '')
    
    # 临时文件
    TEMP_DIR = Path(os.getenv('TEMP_DIR', '/tmp/ragflow_uploads'))
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 日志
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
