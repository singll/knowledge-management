"""Webhook 服务"""
import logging
import json
import requests
from app.models import WebhookHistory
from app.extensions import db

logger = logging.getLogger(__name__)

class WebhookService:
    """Webhook 调用服务"""
    
    @staticmethod
    def trigger_webhook(webhook_config, article_url, extra_data=None):
        """触发 webhook"""
        payload = {
            'article_url': article_url,
            'timestamp': str(datetime.utcnow()),
        }
        if extra_data:
            payload.update(extra_data)
        
        # 创建历史记录
        history = WebhookHistory(
            webhook_id=webhook_config.id,
            article_url=article_url,
            payload=json.dumps(payload),
            status='pending'
        )
        db.session.add(history)
        db.session.commit()
        
        try:
            # 调用 webhook
            response = requests.request(
                method=webhook_config.method,
                url=webhook_config.url,
                json=payload,
                timeout=30
            )
            
            # 更新历史记录
            history.status = 'success' if response.ok else 'failed'
            history.response_code = response.status_code
            history.response_body = response.text[:1000]  # 限制长度
            
        except Exception as e:
            logger.error(f"Webhook 调用失败: {e}")
            history.status = 'failed'
            history.error_message = str(e)
        
        db.session.commit()
        return history.to_dict()
