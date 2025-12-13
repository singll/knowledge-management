"""标签管理 API"""
import logging
from flask import Blueprint, request
from app.models import Tag
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('tags', __name__)
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def list_tags():
    """获取标签列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        keyword = request.args.get('keyword', '').strip()
        
        query = Tag.query
        if keyword:
            query = query.filter(Tag.name.contains(keyword))
        
        pagination = query.order_by(Tag.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [tag.to_dict() for tag in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)
        
    except Exception as e:
        logger.error(f"获取标签列表失败: {e}", exc_info=True)
        return error(f'获取标签列表失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    """获取单个标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)
        
        return success(tag.to_dict())
        
    except Exception as e:
        logger.error(f"获取标签失败: {e}", exc_info=True)
        return error(f'获取标签失败: {str(e)}', status_code=500)


@bp.route('', methods=['POST'])
def create_tag():
    """创建标签"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return error('标签名称不能为空', status_code=400)
        
        # 检查是否已存在
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            return error('标签已存在', status_code=400)
        
        tag = Tag(
            name=name,
            description=data.get('description', '').strip(),
            color=data.get('color', '#409EFF')
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return success(tag.to_dict(), '创建成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建标签失败: {e}", exc_info=True)
        return error(f'创建标签失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """更新标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)
        
        data = request.get_json()
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error('标签名称不能为空', status_code=400)
            # 检查名称是否重复
            existing = Tag.query.filter(Tag.name == name, Tag.id != tag_id).first()
            if existing:
                return error('标签名称已存在', status_code=400)
            tag.name = name
        
        if 'description' in data:
            tag.description = data['description'].strip()
        
        if 'color' in data:
            tag.color = data['color']
        
        db.session.commit()
        
        return success(tag.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新标签失败: {e}", exc_info=True)
        return error(f'更新标签失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """删除标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)
        
        db.session.delete(tag)
        db.session.commit()
        
        return success(None, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除标签失败: {e}", exc_info=True)
        return error(f'删除标签失败: {str(e)}', status_code=500)
