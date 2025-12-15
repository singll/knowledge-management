"""Webhook 管理 API"""
import logging
from datetime import datetime
from flask import Blueprint, request
from app.models import WebhookConfig, WebhookHistory
from app.services.webhook_service import WebhookService
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@bp.route('/configs', methods=['GET'])
def list_webhook_configs():
    """获取 Webhook 配置列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        is_active = request.args.get('is_active')
        
        query = WebhookConfig.query
        
        if is_active in ('true', 'false'):
            query = query.filter_by(is_active=is_active == 'true')
        
        pagination = query.order_by(WebhookConfig.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [wh.to_dict() for wh in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)
        
    except Exception as e:
        logger.error(f"获取Webhook配置列表失败: {e}", exc_info=True)
        return error(f'获取Webhook配置列表失败: {str(e)}', status_code=500)


@bp.route('/configs/<int:config_id>', methods=['GET'])
def get_webhook_config(config_id):
    """获取单个 Webhook 配置"""
    try:
        wh = WebhookConfig.query.get(config_id)
        if not wh:
            return error('Webhook配置不存在', status_code=404)
        
        return success(wh.to_dict())
        
    except Exception as e:
        logger.error(f"获取Webhook配置失败: {e}", exc_info=True)
        return error(f'获取Webhook配置失败: {str(e)}', status_code=500)


@bp.route('/configs', methods=['POST'])
def create_webhook_config():
    """创建 Webhook 配置"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        if not name or not url:
            return error('名称和URL不能为空', status_code=400)
        
        wh = WebhookConfig(
            name=name,
            url=url,
            method=data.get('method', 'POST').upper(),
            description=data.get('description', '').strip(),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(wh)
        db.session.commit()
        
        return success(wh.to_dict(), '创建成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建Webhook配置失败: {e}", exc_info=True)
        return error(f'创建Webhook配置失败: {str(e)}', status_code=500)


@bp.route('/configs/<int:config_id>', methods=['PUT'])
def update_webhook_config(config_id):
    """更新 Webhook 配置"""
    try:
        wh = WebhookConfig.query.get(config_id)
        if not wh:
            return error('Webhook配置不存在', status_code=404)
        
        data = request.get_json()
        
        if 'name' in data:
            wh.name = data['name'].strip()
        if 'url' in data:
            wh.url = data['url'].strip()
        if 'method' in data:
            wh.method = data['method'].upper()
        if 'description' in data:
            wh.description = data['description'].strip()
        if 'is_active' in data:
            wh.is_active = data['is_active']
        
        db.session.commit()
        
        return success(wh.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新Webhook配置失败: {e}", exc_info=True)
        return error(f'更新Webhook配置失败: {str(e)}', status_code=500)


@bp.route('/configs/<int:config_id>', methods=['DELETE'])
def delete_webhook_config(config_id):
    """删除 Webhook 配置"""
    try:
        wh = WebhookConfig.query.get(config_id)
        if not wh:
            return error('Webhook配置不存在', status_code=404)
        
        db.session.delete(wh)
        db.session.commit()
        
        return success(None, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除Webhook配置失败: {e}", exc_info=True)
        return error(f'删除Webhook配置失败: {str(e)}', status_code=500)


@bp.route('/trigger', methods=['POST'])
def trigger_webhook():
    """触发 Webhook"""
    try:
        data = request.get_json()
        config_id = data.get('webhook_id')
        article_url = data.get('article_url', '').strip()
        
        if not config_id or not article_url:
            return error('webhook_id 和 article_url 不能为空', status_code=400)
        
        wh = WebhookConfig.query.get(config_id)
        if not wh:
            return error('Webhook配置不存在', status_code=404)
        
        if not wh.is_active:
            return error('Webhook已禁用', status_code=400)
        
        # 触发 webhook
        result = WebhookService.trigger_webhook(
            wh, 
            article_url, 
            data.get('extra_data')
        )
        
        return success(result, 'Webhook已触发')
        
    except Exception as e:
        logger.error(f"触发Webhook失败: {e}", exc_info=True)
        return error(f'触发Webhook失败: {str(e)}', status_code=500)


@bp.route('/history', methods=['GET'])
def list_webhook_history():
    """获取 Webhook 调用历史"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        webhook_id = request.args.get('webhook_id')
        status = request.args.get('status')
        
        query = WebhookHistory.query
        
        if webhook_id:
            query = query.filter_by(webhook_id=int(webhook_id))
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(WebhookHistory.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [h.to_dict() for h in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)
        
    except Exception as e:
        logger.error(f"获取Webhook历史失败: {e}", exc_info=True)
        return error(f'获取Webhook历史失败: {str(e)}', status_code=500)


@bp.route('/history/<int:history_id>', methods=['GET'])
def get_webhook_history(history_id):
    """获取单条 Webhook 历史"""
    try:
        history = WebhookHistory.query.get(history_id)
        if not history:
            return error('历史记录不存在', status_code=404)
        
        return success(history.to_dict())
        
    except Exception as e:
        logger.error(f"获取Webhook历史失败: {e}", exc_info=True)
        return error(f'获取Webhook历史失败: {str(e)}', status_code=500)
