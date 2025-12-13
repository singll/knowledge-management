"""API 蓝图注册"""
from flask import Blueprint

def register_blueprints(app):
    """注册所有蓝图"""
    from app.api.ragflow import bp as ragflow_bp
    from app.api.dataset import bp as dataset_bp
    from app.api.tags import bp as tags_bp
    from app.api.datasource import bp as datasource_bp
    from app.api.rss import bp as rss_bp
    from app.api.webhook import bp as webhook_bp
    
    app.register_blueprint(ragflow_bp, url_prefix='/api/ragflow')
    app.register_blueprint(dataset_bp, url_prefix='/api/ragflow')  # 共用 ragflow 前缀
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(datasource_bp, url_prefix='/api/datasources')
    app.register_blueprint(rss_bp, url_prefix='/api/rss')
    app.register_blueprint(webhook_bp, url_prefix='/api/webhooks')
