"""数据源管理 API"""
import logging
from flask import Blueprint, request
from app.models import DataSource, Tag
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('datasource', __name__)
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def list_datasources():
    """获取数据源列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category', '').strip()
        is_active = request.args.get('is_active')
        
        query = DataSource.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    DataSource.name.contains(keyword),
                    DataSource.url.contains(keyword)
                )
            )
        
        if category:
            query = query.filter_by(category=category)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active == 'true')
        
        pagination = query.order_by(DataSource.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [ds.to_dict() for ds in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)
        
    except Exception as e:
        logger.error(f"获取数据源列表失败: {e}", exc_info=True)
        return error(f'获取数据源列表失败: {str(e)}', status_code=500)


@bp.route('/<int:datasource_id>', methods=['GET'])
def get_datasource(datasource_id):
    """获取单个数据源"""
    try:
        ds = DataSource.query.get(datasource_id)
        if not ds:
            return error('数据源不存在', status_code=404)
        
        return success(ds.to_dict())
        
    except Exception as e:
        logger.error(f"获取数据源失败: {e}", exc_info=True)
        return error(f'获取数据源失败: {str(e)}', status_code=500)


@bp.route('', methods=['POST'])
def create_datasource():
    """创建数据源"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        if not name or not url:
            return error('名称和URL不能为空', status_code=400)
        
        ds = DataSource(
            name=name,
            url=url,
            type=data.get('type', 'website'),
            category=data.get('category', '').strip(),
            description=data.get('description', '').strip(),
            is_active=data.get('is_active', True)
        )
        
        # 处理标签
        tag_ids = data.get('tag_ids', [])
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            ds.tags = tags
        
        db.session.add(ds)
        db.session.commit()
        
        return success(ds.to_dict(), '创建成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建数据源失败: {e}", exc_info=True)
        return error(f'创建数据源失败: {str(e)}', status_code=500)


@bp.route('/<int:datasource_id>', methods=['PUT'])
def update_datasource(datasource_id):
    """更新数据源"""
    try:
        ds = DataSource.query.get(datasource_id)
        if not ds:
            return error('数据源不存在', status_code=404)
        
        data = request.get_json()
        
        if 'name' in data:
            ds.name = data['name'].strip()
        if 'url' in data:
            ds.url = data['url'].strip()
        if 'type' in data:
            ds.type = data['type']
        if 'category' in data:
            ds.category = data['category'].strip()
        if 'description' in data:
            ds.description = data['description'].strip()
        if 'is_active' in data:
            ds.is_active = data['is_active']
        
        # 更新标签
        if 'tag_ids' in data:
            tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
            ds.tags = tags
        
        db.session.commit()
        
        return success(ds.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新数据源失败: {e}", exc_info=True)
        return error(f'更新数据源失败: {str(e)}', status_code=500)


@bp.route('/<int:datasource_id>', methods=['DELETE'])
def delete_datasource(datasource_id):
    """删除数据源"""
    try:
        ds = DataSource.query.get(datasource_id)
        if not ds:
            return error('数据源不存在', status_code=404)
        
        db.session.delete(ds)
        db.session.commit()
        
        return success(None, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除数据源失败: {e}", exc_info=True)
        return error(f'删除数据源失败: {str(e)}', status_code=500)
