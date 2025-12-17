"""Webhook 服务"""
import logging
import json
import time
import re
import requests
from datetime import datetime
from app.models import WebhookHistory
from app.extensions import db

logger = logging.getLogger(__name__)


class WebhookService:
    """Webhook 调用服务"""

    @staticmethod
    def process_template(template_str, variables):
        """处理模板字符串，替换变量"""
        if not template_str:
            return template_str

        result = template_str
        for key, value in variables.items():
            # 支持 {{variable}} 格式
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            result = re.sub(pattern, str(value) if value is not None else '', result)

        return result

    @staticmethod
    def trigger_webhook(webhook_config, request_body=None):
        """触发 webhook

        Args:
            webhook_config: WebhookConfig 对象
            request_body: 自定义请求体（字典），如果为None则使用配置的模板
        """
        # 准备变量
        now = datetime.utcnow()
        variables = {
            'timestamp': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'webhook_name': webhook_config.name,
            'article_url': '',  # 保持兼容
        }

        # 处理请求体
        if request_body is not None:
            # 使用传入的请求体
            payload = request_body
            # 处理请求体中的变量
            if isinstance(payload, dict):
                for key, value in payload.items():
                    if isinstance(value, str):
                        payload[key] = WebhookService.process_template(value, variables)
                        # 更新 article_url 变量
                        if key == 'url' or key == 'article_url':
                            variables['article_url'] = payload[key]
        elif webhook_config.body_template:
            # 使用配置的模板
            try:
                template_str = WebhookService.process_template(
                    webhook_config.body_template, variables
                )
                payload = json.loads(template_str)
            except json.JSONDecodeError as e:
                logger.error(f"请求体模板JSON解析失败: {e}")
                payload = {'error': '模板解析失败', 'raw': webhook_config.body_template}
        else:
            # 默认请求体
            payload = {
                'timestamp': variables['timestamp'],
                'webhook_name': variables['webhook_name'],
                'source': 'knowledge-management'
            }

        # 处理请求头
        headers = {'Content-Type': webhook_config.content_type or 'application/json'}
        if webhook_config.headers:
            try:
                custom_headers = json.loads(webhook_config.headers)
                if isinstance(custom_headers, dict):
                    # 处理请求头中的变量
                    for key, value in custom_headers.items():
                        if isinstance(value, str):
                            custom_headers[key] = WebhookService.process_template(value, variables)
                    headers.update(custom_headers)
            except json.JSONDecodeError:
                logger.warning(f"自定义请求头JSON解析失败，使用默认请求头")

        # 创建历史记录
        history = WebhookHistory(
            webhook_id=webhook_config.id,
            request_url=webhook_config.url,
            request_method=webhook_config.method,
            request_headers=json.dumps(headers, ensure_ascii=False),
            payload=json.dumps(payload, ensure_ascii=False) if payload else None,
            article_url=variables.get('article_url', ''),
            status='pending'
        )
        db.session.add(history)
        db.session.commit()

        start_time = time.time()

        try:
            # 准备请求参数
            request_kwargs = {
                'method': webhook_config.method,
                'url': webhook_config.url,
                'headers': headers,
                'timeout': webhook_config.timeout or 30
            }

            # 根据Content-Type设置请求体
            content_type = (webhook_config.content_type or 'application/json').lower()
            if webhook_config.method.upper() in ['POST', 'PUT', 'PATCH']:
                if 'application/json' in content_type:
                    request_kwargs['json'] = payload
                elif 'application/x-www-form-urlencoded' in content_type:
                    request_kwargs['data'] = payload
                else:
                    request_kwargs['data'] = json.dumps(payload) if isinstance(payload, dict) else payload

            # 发送请求
            response = requests.request(**request_kwargs)

            # 计算耗时
            duration = int((time.time() - start_time) * 1000)

            # 更新历史记录
            history.status = 'success' if response.ok else 'failed'
            history.response_code = response.status_code
            history.response_headers = json.dumps(dict(response.headers), ensure_ascii=False)
            history.response_body = response.text[:5000]  # 限制长度
            history.duration = duration

            if not response.ok:
                history.error_message = f"HTTP {response.status_code}: {response.reason}"

        except requests.exceptions.Timeout:
            duration = int((time.time() - start_time) * 1000)
            history.status = 'failed'
            history.error_message = f"请求超时 (>{webhook_config.timeout or 30}秒)"
            history.duration = duration
            logger.error(f"Webhook 请求超时: {webhook_config.url}")

        except requests.exceptions.ConnectionError as e:
            duration = int((time.time() - start_time) * 1000)
            history.status = 'failed'
            history.error_message = f"连接失败: {str(e)}"
            history.duration = duration
            logger.error(f"Webhook 连接失败: {e}")

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            history.status = 'failed'
            history.error_message = str(e)
            history.duration = duration
            logger.error(f"Webhook 调用失败: {e}")

        db.session.commit()
        return history.to_dict()
