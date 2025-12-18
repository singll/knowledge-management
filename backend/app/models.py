"""数据库模型"""
from datetime import datetime
from app.extensions import db

class Tag(db.Model):
    """标签表"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    color = db.Column(db.String(20), default='#409EFF')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DataSource(db.Model):
    """数据源表"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), default='website')  # website, api, rss
    category = db.Column(db.String(50))  # tech, news, blog
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联标签（多对多）
    tags = db.relationship('Tag', secondary='datasource_tags', backref='data_sources')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RSSFeed(db.Model):
    """RSS 订阅源表"""
    __tablename__ = 'rss_feeds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联标签
    tags = db.relationship('Tag', secondary='rss_tags', backref='rss_feeds')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
            'last_fetched': self.last_fetched.isoformat() if self.last_fetched else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WebhookConfig(db.Model):
    """Webhook 配置表"""
    __tablename__ = 'webhook_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), default='POST')
    content_type = db.Column(db.String(100), default='application/json')
    headers = db.Column(db.Text)  # JSON格式存储自定义请求头
    body_template = db.Column(db.Text)  # 请求体模板
    timeout = db.Column(db.Integer, default=30)  # 超时时间（秒）
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'method': self.method,
            'content_type': self.content_type,
            'headers': self.headers,
            'body_template': self.body_template,
            'timeout': self.timeout,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WebhookHistory(db.Model):
    """Webhook 调用历史表"""
    __tablename__ = 'webhook_history'

    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhook_configs.id'), nullable=False)
    request_url = db.Column(db.String(500))  # 实际请求的URL
    request_method = db.Column(db.String(10))  # 请求方法
    request_headers = db.Column(db.Text)  # 请求头JSON
    payload = db.Column(db.Text)  # 请求体
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    response_code = db.Column(db.Integer)
    response_headers = db.Column(db.Text)  # 响应头JSON
    response_body = db.Column(db.Text)
    duration = db.Column(db.Integer)  # 请求耗时（毫秒）
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 保留旧字段兼容
    article_url = db.Column(db.String(500))

    webhook = db.relationship('WebhookConfig', backref='history')

    def to_dict(self):
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'webhook_name': self.webhook.name if self.webhook else None,
            'request_url': self.request_url or self.article_url,
            'request_method': self.request_method,
            'request_headers': self.request_headers,
            'article_url': self.article_url,
            'payload': self.payload,
            'status': self.status,
            'response_code': self.response_code,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
            'duration': self.duration,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 多对多关联表
datasource_tags = db.Table('datasource_tags',
    db.Column('datasource_id', db.Integer, db.ForeignKey('data_sources.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

rss_tags = db.Table('rss_tags',
    db.Column('rss_id', db.Integer, db.ForeignKey('rss_feeds.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class DatasetMapping(db.Model):
    """知识库映射表 - 用于工作流动态获取知识库ID"""
    __tablename__ = 'dataset_mappings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)  # 映射名称，如 security, news, ai
    display_name = db.Column(db.String(100))  # 显示名称，如 "安全知识库"
    dataset_id = db.Column(db.String(100), nullable=False)  # RagFlow 中的 dataset_id
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认知识库
    is_active = db.Column(db.Boolean, default=True)
    parser_id = db.Column(db.String(50), default='naive')  # 默认解析器
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联标签（多对多）- 表示该知识库关联的标签
    tags = db.relationship('Tag', secondary='dataset_tags', backref='datasets')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'dataset_id': self.dataset_id,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'parser_id': self.parser_id,
            'tags': [tag.to_dict() for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# 知识库-标签关联表
dataset_tags = db.Table('dataset_tags',
    db.Column('dataset_mapping_id', db.Integer, db.ForeignKey('dataset_mappings.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class ArticleTag(db.Model):
    """文章标签关联表 - 记录入库文章与标签的关联"""
    __tablename__ = 'article_tags'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(100), nullable=False, index=True)  # RagFlow 中的 document_id
    dataset_id = db.Column(db.String(100), nullable=False, index=True)  # RagFlow 中的 dataset_id
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    article_title = db.Column(db.String(500))  # 文章标题
    article_url = db.Column(db.String(1000))  # 文章原始URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tag = db.relationship('Tag', backref='article_associations')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'dataset_id': self.dataset_id,
            'tag_id': self.tag_id,
            'tag': self.tag.to_dict() if self.tag else None,
            'article_title': self.article_title,
            'article_url': self.article_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
