"""RSS 订阅源管理 API"""
import logging
from flask import Blueprint, request
from app.models import RSSFeed, Tag
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('rss', __name__)
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def list_rss_feeds():
    """获取 RSS 订阅源列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))  # 改为10，与前端一致
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category', '').strip()
        
        query = RSSFeed.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    RSSFeed.name.contains(keyword),
                    RSSFeed.url.contains(keyword)
                )
            )
        
        if category:
            query = query.filter_by(category=category)
            
        # 添加调试日志
        app.logger.info(f"RSS查询参数: page={page}, per_page={per_page}, keyword={keyword}, category={category}")
        
        pagination = query.order_by(RSSFeed.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [rss.to_dict() for rss in pagination.items]
        
        # 确保返回格式统一
        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": items,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages
            }
        }
        
    except Exception as e:
        logger.error(f"获取RSS列表失败: {e}", exc_info=True)
        return {"code": 500, "message": f'获取RSS列表失败: {str(e)}'}, 500


@bp.route('/<int:rss_id>', methods=['GET'])
def get_rss_feed(rss_id):
    """获取单个 RSS 订阅源"""
    try:
        rss = RSSFeed.query.get(rss_id)
        if not rss:
            return error('RSS订阅源不存在', status_code=404)
        
        return success(rss.to_dict())
        
    except Exception as e:
        logger.error(f"获取RSS失败: {e}", exc_info=True)
        return error(f'获取RSS失败: {str(e)}', status_code=500)


@bp.route('', methods=['POST'])
def create_rss_feed():
    """创建 RSS 订阅源"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        
        if not name or not url:
            return error('名称和URL不能为空', status_code=400)
        
        # 检查URL是否已存在
        existing = RSSFeed.query.filter_by(url=url).first()
        if existing:
            return error('该RSS订阅源已存在', status_code=400)
        
        rss = RSSFeed(
            name=name,
            url=url,
            category=data.get('category', '').strip(),
            description=data.get('description', '').strip(),
            is_active=data.get('is_active', True)
        )
        
        # 处理标签
        tag_ids = data.get('tag_ids', [])
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            rss.tags = tags
        
        db.session.add(rss)
        db.session.commit()
        
        return success(rss.to_dict(), '创建成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建RSS失败: {e}", exc_info=True)
        return error(f'创建RSS失败: {str(e)}', status_code=500)


@bp.route('/<int:rss_id>', methods=['PUT'])
def update_rss_feed(rss_id):
    """更新 RSS 订阅源"""
    try:
        rss = RSSFeed.query.get(rss_id)
        if not rss:
            return error('RSS订阅源不存在', status_code=404)
        
        data = request.get_json()
        
        if 'name' in data:
            rss.name = data['name'].strip()
        if 'url' in data:
            new_url = data['url'].strip()
            # 检查URL是否与其他记录重复
            existing = RSSFeed.query.filter(
                RSSFeed.url == new_url, 
                RSSFeed.id != rss_id
            ).first()
            if existing:
                return error('该RSS订阅源URL已存在', status_code=400)
            rss.url = new_url
        if 'category' in data:
            rss.category = data['category'].strip()
        if 'description' in data:
            rss.description = data['description'].strip()
        if 'is_active' in data:
            rss.is_active = data['is_active']
        
        # 更新标签
        if 'tag_ids' in data:
            tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
            rss.tags = tags
        
        db.session.commit()
        
        return success(rss.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新RSS失败: {e}", exc_info=True)
        return error(f'更新RSS失败: {str(e)}', status_code=500)


@bp.route('/<int:rss_id>', methods=['DELETE'])
def delete_rss_feed(rss_id):
    """删除 RSS 订阅源"""
    try:
        rss = RSSFeed.query.get(rss_id)
        if not rss:
            return error('RSS订阅源不存在', status_code=404)
        
        db.session.delete(rss)
        db.session.commit()
        
        return success(None, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除RSS失败: {e}", exc_info=True)
        return error(f'删除RSS失败: {str(e)}', status_code=500)
